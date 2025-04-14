from typing import Dict, Any
import json
import sys
from functools import lru_cache
from apig_wsgi import make_lambda_handler

# LOGS at https://msdlive-gridcerfapp-logs.s3.amazonaws.com/

# SOURCED SCRIPT
# from dash_app.app import app
# from dash_app.layout import create_app
from test_app import create_app

@lru_cache(maxsize=5)
def build_handler(url_prefix: str) -> "Dash":

    # If there's no prefix, it's a custom domain
    if url_prefix is None or url_prefix == "":
        return make_lambda_handler(wsgi_app=create_app().server, binary_support=True)

    # If there's a prefix we're dealing with an API gateway stage
    # and need to return the appropriate urls.
    return make_lambda_handler(
        wsgi_app=create_app({"url_base_pathname": url_prefix}).server,
        binary_support=True,
    )


def get_raw_path(apigw_event: dict) -> str:
    return apigw_event.get("requestContext", {}).get("path", apigw_event["path"])


def get_url_prefix(apigw_event: dict) -> str:
    apigw_stage_name = apigw_event["requestContext"]["stage"]
    prefix = f"/{apigw_stage_name}/"
    raw_path = get_raw_path(apigw_event)
    if raw_path.startswith(prefix):
        return prefix
    return ""


def lambda_handler(
    event: dict[str, "Any"], context: dict[str, "Any"]
) -> dict[str, "Any"]:
    event["path"] = get_raw_path(event)
    handle_event = build_handler(get_url_prefix(event))
    response = handle_event(event, context)
    return response

