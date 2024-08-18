from flask import render_template
from app import app, db


@app.errorhandler(404)
def not_found_error(error):
    """
    Handle 404 Not Found error.

    This function is triggared when a 404 error occurs, which means the
    requested resource could not be found.
    It renders a custom 404 error page.

    Args:
        error: The error object containing details about the 404 error.

    Returns:
        A tuple containing the rendered 404 error page and the 404 status code
    """
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """
    Handle 500 Internal Server Error.

    This function is triggered when a 500 error occurs, which means there was
    an internal server error.
    It rolls back the current database session to avoid an inconsistent state
    and renders a custom 500 error page.

    Args:
        error:The error object containingdetails about the 500 error.

    Returns:
        A tuple containing the rendered 500 error page and the 500 status code
    """
    db.session.rollback()
    return render_template('500.html'), 500
