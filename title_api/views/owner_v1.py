import json
from flask import Blueprint, Response, current_app, request
from flask_negotiate import produces
from title_api.exceptions import ApplicationError
from title_api.models import Owner

# This is the blueprint object that gets registered into the app in blueprints.py.
owner_v1 = Blueprint('owner_v1', __name__)


@owner_v1.route("/owners", methods=["GET"])
@produces("application/json")
def get_owner():
    """Get an Owner by email_address."""
    current_app.logger.info('Starting get_owner method')

    response = []

    # Get filters
    email_address = request.args.get('email_address')

    if email_address:
        owner_result = Owner.query.filter_by(email=email_address).first()
    else:
        raise ApplicationError("'email_address' is required.", "E001", 400)

    if owner_result:
        response.append(owner_result.as_dict())

    return Response(response=json.dumps(response, sort_keys=True, separators=(',', ':')),
                    mimetype='application/json', status=200)
