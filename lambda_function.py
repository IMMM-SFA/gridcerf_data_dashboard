from typing import Dict, Any
import json
import sys
from functools import lru_cache
from apig_wsgi import make_lambda_handler

# SOURCED SCRIPT
# from dash_app.app import app
from dash_app.layout import create_app

@lru_cache(maxsize=5)
def get_wsgi_handler():
    """Wrap this method in an lru_cache so if the lambda container is reused, the handler
    doesn't have to be recreated.

    Returns:
        _type_: lambda handler that is wsgi compatible and backed by the Dash application
    """
    return make_lambda_handler(
        wsgi_app=create_app().server,
        # wsgi_app=app.server,
        binary_support=True,
    )


def lambda_handler(event: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    # print("Received request:", json.dumps(event))
    handle_event = get_wsgi_handler()
    response = handle_event(event, context)
    # response_size = sys.getsizeof(json.dumps(response))
    # print("Response body size:", response_size, "bytes")
    return response
