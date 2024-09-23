import sqlalchemy as sa
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth

from app import db
from app.models import User
from app.api.errors import error_response

# Initialize HTTP Basic and Token authentication
basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

@basic_auth.verify_password
def verify_password(username, password):
    """
    Verify the user's password.

    Args:
        username (str): The username of the user.
        password (str): The password of the user.

    Returns:
        User: The authenticated user object if credentials are valid, else None.
    """
    user = db.session.scalar(sa.select(User).where(User.username == username))
    if user and user.check_password(password):
        return user

@basic_auth.error_handler
def basic_auth_error(status):
    """
    Handle errors for basic authentication.

    Args:
        status (int): The HTTP status code.

    Returns:
        Response: The error response.
    """
    return error_response(status)

@token_auth.verify_token
def verify_token(token):
    """
    Verify the user's token.

    Args:
        token (str): The token of the user.

    Returns:
        User: The authenticated user object if token is valid, else None.
    """
    return User.check_token(token) if token else None

@token_auth.error_handler
def token_auth_error(status):
    """
    Handle errors for token authentication.

    Args:
        status (int): The HTTP status code.

    Returns:
        Response: The error response.
    """
    return error_response(status)