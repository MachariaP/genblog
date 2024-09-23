from flask import render_template, request

from app import db
from app.errors import bp
from app.api.errors import error_response as api_error_response


def wants_json_response():
    """
    Determine if the client prefers a JSON response.

    Returns:
        bool: True if the client prefers a JSON response, False otherwise.
    """
    return request.accept_mimetypes[
            'application/json'] >= request.accept_mimetypes['text/html']


@bp.app_errorhandler(404)
def not_found_error(error):
    """
    Handle 404 Not Found errors.

    Args:
        error (HTTPException): The error that occurred.

    Returns:
        Response: The error response, either JSON or HTML.
    """
    if wants_json_response():
        return api_error_response(404)
    return render_template('errors/404.html'), 404


@bp.app_errorhandler(500)
def internal_error(error):
    """
    Handle 500 Internal Server errors.

    Args:
        error (HTTPException): The error that occurred.

    Returns:
        Response: The error response, either JSON or HTML.
    """
    db.session.rollback()
    if wants_json_response():
        return api_error_response(500)
    return render_template('errors/500.html'), 500
