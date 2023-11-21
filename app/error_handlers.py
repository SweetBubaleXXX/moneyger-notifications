import json

from werkzeug.exceptions import HTTPException


def handle_http_exception(exc: HTTPException):
    response = exc.get_response()
    response.data = json.dumps(
        {
            "message": exc.description,
        }
    )
    response.content_type = "application/json"
    return response
