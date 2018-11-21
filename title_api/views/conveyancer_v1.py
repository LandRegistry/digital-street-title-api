import json

from flask import Blueprint, Response, current_app
from flask_negotiate import produces

from title_api.exceptions import ApplicationError
from title_api.models import Conveyancer

# This is the blueprint object that gets registered into the app in blueprints.py.
conveyancer_v1 = Blueprint('conveyancer_v1', __name__)


@conveyancer_v1.route("/conveyancers", methods=["GET"])
@produces("application/json")
def get_conveyancers():
    """Get Conveyancers"""

    current_app.logger.info('Starting get_conveyancers method')
    results = []

    query_result = Conveyancer.query.all()

    # Format/Process
    for item in query_result:
        results.append(item.as_dict())

    # Output
    return Response(response=json.dumps(results, sort_keys=True, separators=(',', ':')),
                    mimetype='application/json', status=200)


@conveyancer_v1.route("/conveyancers/<int:conveyancer_id>", methods=["GET"])
@produces("application/json")
def get_conveyancer(conveyancer_id):
    """Get Conveyancer for a given conveyancer_id"""

    current_app.logger.info('Starting get_conveyancer method')

    # Query DB
    query_result = Conveyancer.query.get(conveyancer_id)

    # Throw if not found
    if not query_result:
        raise ApplicationError("A conveyancer with the specified conveyancer ID was not found.", "E002", 404)

        # Format/Process
    result = query_result.as_dict()

    # Output
    return Response(response=json.dumps(result, sort_keys=True, separators=(',', ':')),
                    mimetype='application/json', status=200)
