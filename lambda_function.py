from typing import Dict, Any

from functools import lru_cache

from apig_wsgi import make_lambda_handler

from dash_app.app import create_app


@lru_cache(maxsize=5)
def get_wsgi_handler():
    """We wrap this method in an lru_cache (least recently used) so if the lambda 
    function is reused before shutting down, the handler doesn't have to be recreated.

    Returns:
        func: lambda handler that is wsgi compatible and backed by the Dash application
    """
    return make_lambda_handler(wsgi_app=create_app().server, binary_support=True)


def lambda_handler(event: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """This is the real lambda handler called by AWS.  We map it onto WSGI and then
    call the Dash Flask application via the WSGI interface.

    Args:
        event (Dict[str, Any]): _description_
        context (Dict[str, Any]): _description_

    Returns:
        Dict[str, Any]: _description_
    """

    handle_event = get_wsgi_handler()
    response = handle_event(event, context)
    return response
