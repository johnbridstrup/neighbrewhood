from enum import Enum
from ninja import Schema
from typing import Dict


class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PATCH = "PATCH"
    PUT = "PUT"
    DELETE = "DELETE"
    HEAD = "HEAD"


class DefaultError(Schema):
    detail: str


class DefaultSuccess(Schema):
    message: str


class ActionUrlSchema(Schema):
    method: HttpMethod
    url: str
    schema: dict = None

def make_action(method: HttpMethod, url, schema=None):
    ret = {
        "method": method.value,
        "url": url,
    }

    if schema:
        ret["schema"] = schema
    
    return ret
