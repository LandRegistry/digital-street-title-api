import datetime
import json

from flask import Blueprint, Response, current_app, request
from flask_negotiate import consumes, produces
from jsonschema import FormatChecker, RefResolver, ValidationError, validate
from sqlalchemy import exc
from title_api.exceptions import ApplicationError
from title_api.extensions import db
from title_api.models import Address, Owner, Title

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

    if owner_email_address:
        owner_result = Owner.query.filter_by(email=owner_email_address.lower()).first()
        title_result = Title.query.filter_by(owner=owner_result).all()
    else:
        raise ApplicationError("'owner_email_address' is required.", "E001", 400)

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
