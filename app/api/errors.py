from werkzeug.http import HTTP_STATUS_CODES
from werkzeug.exceptions import HTTPException

from app.api import bp

def error_response(status_code, message=None):
    """
    Generate an error response.

    Args:
        status_code (int): The HTTP status code.
        message (str, optional): Additional message to include in the response.

    Returns:
        tuple: A tuple containing the payload dictionary and the status code.
    """
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    return payload, status_code

def bad_request(message):
    """
    Generate a 400 Bad Request error response.

    Args:
        message (str): The message to include in the response.

    Returns:
        tuple: A tuple containing the payload dictionary and the status code.
    """
    return error_response(400, message)

@bp.errorhandler(HTTPException)
def handle_exception(e):
    """
    Handle HTTP exceptions and generate an error response.

    Args:
        e (HTTPException): The HTTP exception.

    Returns:
        tuple: A tuple containing the payload dictionary and the status code.
    """
    return error_response(e.code)