import datetime
import json
from flask import Blueprint, Response, current_app, request
from flask_negotiate import consumes, produces
from jsonschema import FormatChecker, RefResolver, ValidationError, validate
from sqlalchemy import exc
from title_api.exceptions import ApplicationError
from title_api.extensions import db
from title_api.models import Address, Owner, Title, Charge, Restriction

# This is the blueprint object that gets registered into the app in blueprints.py.
title_v1 = Blueprint('title_v1', __name__)

openapi_filepath = 'openapi.json'

# JSON schema for title requests
with open(openapi_filepath) as json_file:
    openapi = json.load(json_file)

ref_resolver = RefResolver(openapi_filepath, openapi)
title_request_schema = openapi["components"]["schemas"]["TitleRequest"]

days_to_lock_title_for = 30


@title_v1.route("/titles", methods=["GET"])
@produces("application/json")
def get_titles():
    """Get a list of Titles by Owner's email_address."""
    current_app.logger.info('Starting get_titles method')
    results = []

    # Get filters
    owner_email_address = request.args.get('owner_email_address')
    owner_identity = request.args.get('owner_identity')
    address_house_name_number = request.args.get('address_house_name_number')
    address_postcode = request.args.get('address_postcode')

    if owner_email_address:
        owner_result = Owner.query.filter_by(email=owner_email_address.lower()).first()
        title_result = Title.query.filter_by(owner=owner_result)
    elif owner_identity:
        owner_result = Owner.query.filter_by(identity=owner_identity).first()
        title_result = Title.query.filter_by(owner=owner_result)
    else:
        raise ApplicationError("`owner_identity` or `owner_email_address` is required.", "E001", 400)

    if address_house_name_number and address_postcode:
        address_result = Address.query.filter_by(house_name_or_number=address_house_name_number)
        address_result = address_result.filter_by(postcode=address_postcode)
        address_result = address_result.first()
        title_result = title_result.filter_by(address=address_result).limit(1)
    elif bool(address_house_name_number) != bool(address_postcode):  # XOR
        raise ApplicationError("`address_house_name_number` AND `address_postcode` are required", "E001", 400)

    # Finalise db query
    title_result = title_result.all()

    # Build JSON
    for item in title_result:
        results.append(item.as_dict())

    return Response(response=json.dumps(results, sort_keys=True, separators=(',', ':')),
                    mimetype='application/json', status=200)


@title_v1.route("/titles/<string:title_number>", methods=["GET"])
@produces("application/json")
def get_title(title_number):
    """Get a Title for a given title_number."""
    current_app.logger.info('Starting get_title method')

    # Query DB
    query_result = Title.query.get(title_number)

    # Throw if not found
    if not query_result:
        raise ApplicationError("A title with the specified title number was not found.", "E002", 404)

    # Format/Process
    result = query_result.as_dict()

    # Output
    return Response(response=json.dumps(result, sort_keys=True, separators=(',', ':')),
                    mimetype='application/json', status=200)


@title_v1.route("/titles/<string:title_number>", methods=["PUT"])
@consumes("application/json")
@produces("application/json")
def update_title(title_number):
    """Update the Owner of a Title."""
    title_request = request.json
    current_app.logger.info('Starting update_title: {}'.format(title_number))

    # Validate input
    try:
        validate(title_request, title_request_schema, format_checker=FormatChecker(), resolver=ref_resolver)
    except ValidationError as e:
        raise ApplicationError(e.message, "E001", 400)

    # Get the existing title
    title = Title.query.get(title_number)

    # Check that the title exists
    if not title:
        raise ApplicationError("A title with the specified title number was not found.", 'E404', 404)

    # Check that the title numbers match
    if not (title.title_number == title_number):
        raise ApplicationError('Title Number mismatch.', 'E004', 400)

    # Check that the title isn't locked
    if title.lock and title.lock > datetime.datetime.utcnow():
        raise ApplicationError("Title is locked until " + str(title.lock), "E403", 403)

    # Modify title
    title.updated_at = datetime.datetime.utcnow()

    # Modify restrictions
    restrictions_search_list_dict = {}
    restrictions_search_list = {}
    for restriction in title.restrictions:
        restriction_dict = restriction.as_dict()
        restrictions_search_list_id = ''.join([
            restriction_dict['restriction_type'],
            restriction_dict['restriction_id'],
            restriction_dict['date']
        ])
        restrictions_search_list_dict[restrictions_search_list_id] = restriction_dict
        restrictions_search_list[restrictions_search_list_id] = restriction

    for new_restriction in title_request['restrictions']:
        if Restriction.from_dict(new_restriction, title_number).as_dict() in restrictions_search_list.values():
            # It exists!
            # Remove from search list
            restrictions_search_list_id = ''.join([
                new_restriction['restriction_type'],
                new_restriction['restriction_id'],
                new_restriction['date']
            ])
            del restrictions_search_list_dict[restrictions_search_list_id]
            del restrictions_search_list[restrictions_search_list_id]
        else:
            charge = None
            if 'charge' in new_restriction:
                # Add new charge for restriction
                charge = Charge(
                    new_restriction['charge']['date'],
                    new_restriction['charge']['lender'],
                    new_restriction['charge']['amount'],
                    new_restriction['charge']['amount_currency_code'],
                    title_number
                )

                db.session.add(charge)

            # Add new restriction
            restriction = Restriction(
                new_restriction['date'],
                new_restriction['restriction_id'],
                new_restriction['restriction_type'],
                new_restriction['restriction_text'],
                new_restriction['consenting_party'],
                title_number
            )
            if 'charge' in new_restriction:
                restriction.charge = charge

            db.session.add(restriction)

    # Remove old restrictions
    for old_restriction in restrictions_search_list.values():
        if old_restriction.charge:
            title.charges.remove(old_restriction.charge)
            db.session.delete(old_restriction.charge)
        title.restrictions.remove(old_restriction)
        db.session.delete(old_restriction)

    # Modify charges
    charges_search_list_dict = {}
    charges_search_list = {}
    for charge in title.charges:
        if not charge.restriction:
            charge_dict = charge.as_dict()
            charges_search_list_id = ''.join([
                charge_dict['lender_string'],
                str(charge_dict['amount']),
                charge_dict['amount_currency_code'],
                charge_dict['date']
            ])
            charges_search_list_dict[charges_search_list_id] = charge_dict
            charges_search_list[charges_search_list_id] = charge

    for new_charge in title_request['charges']:
        if Charge.from_dict(new_charge, title_number).as_dict() in charges_search_list.values():
            # It exists!
            # Remove from search list
            charges_search_list_id = ''.join([
                new_charge['lender_string'],
                str(new_charge['amount']),
                new_charge['amount_currency_code'],
                new_charge['date']
            ])
            del charges_search_list_dict[charges_search_list_id]
            del charges_search_list[charges_search_list_id]
        else:
            # Add new charge
            charge = Charge(
                new_charge['date'],
                new_charge['lender'],
                new_charge['amount'],
                new_charge['amount_currency_code'],
                title_number
            )
            db.session.add(charge)

    # Remove old charges
    for old_charge in charges_search_list.values():
        title.charges.remove(old_charge)
        db.session.delete(old_charge)

    # Modify owner
    # Check if the owner id has changed, and if so check whether the new owner id exists
    if not title_request['owner']['identity'] == title.owner.identity:
        owner = Owner.query.get(title_request['owner']['identity'])
        # Check if the new owner already exists, and if not create them
        if not owner:
            owner_address = Address(
                title_request['owner']['address']['house_name_number'],
                title_request['owner']['address']['street'],
                title_request['owner']['address']['town_city'],
                title_request['owner']['address']['county'],
                title_request['owner']['address']['country'],
                title_request['owner']['address']['postcode']
            )
            db.session.add(owner_address)

            owner = Owner(
                title_request['owner']['identity'],
                title_request['owner']['first_name'],
                title_request['owner']['last_name'],
                title_request['owner']['email_address'],
                title_request['owner']['phone_number'],
                title_request['owner']['type'],
                owner_address
            )
            db.session.add(owner)
        title.owner = owner
    else:
        owner_address = title.owner.address
        owner_address.house_name_or_number = title_request['owner']['address']['house_name_number']
        owner_address.street_name = title_request['owner']['address']['street']
        owner_address.city = title_request['owner']['address']['town_city']
        owner_address.county = title_request['owner']['address']['county']
        owner_address.country = title_request['owner']['address']['country']
        owner_address.postcode = title_request['owner']['address']['postcode']
        db.session.add(owner_address)

        owner = title.owner
        owner.identity = title_request['owner']['identity']
        owner.forename = title_request['owner']['first_name']
        owner.surname = title_request['owner']['last_name']
        owner.email = title_request['owner']['email_address']
        owner.phone = title_request['owner']['phone_number']
        owner.owner_type = title_request['owner']['type']
        owner.address = owner_address
        db.session.add(owner)

    db.session.add(title)

    try:
        db.session.commit()
    except exc.IntegrityError:
        raise ApplicationError("Owner's email address is already in use.", 'E003', 409)

    return Response(response=repr(title), mimetype='application/json', status=200)


@title_v1.route("/titles/<string:title_number>/lock", methods=["PUT"])
@produces("application/json")
def lock_title(title_number):
    """Lock a Title for a given title_number."""
    current_app.logger.info('Starting lock_title: {}'.format(title_number))

    title = Title.query.get(title_number)

    if not title:
        raise ApplicationError("A title with the specified title number was not found.", 'E404', 404)

    if title.lock and title.lock > datetime.datetime.utcnow():
        raise ApplicationError("The title is already locked.", 'E409', 409)

    title.lock = (datetime.datetime.utcnow() + datetime.timedelta(days=days_to_lock_title_for)).isoformat()

    db.session.add(title)
    db.session.commit()

    return Response(response=repr(title), mimetype='application/json', status=200)


@title_v1.route("/titles/<string:title_number>/unlock", methods=["PUT"])
@produces("application/json")
def unlock_title(title_number):
    """Unlock a Title for a given title_number."""
    current_app.logger.info('Starting unlock_title: {}'.format(title_number))

    title = Title.query.get(title_number)

    if not title:
        raise ApplicationError("A title with the specified title number was not found.", 'E404', 404)

    if not title.lock:
        raise ApplicationError("The title is already unlocked.", 'E409', 409)

    title.lock = None

    db.session.add(title)
    db.session.commit()

    return Response(response=repr(title), mimetype='application/json', status=200)
