from app import db
from app.api import bp
from app.api.auth import basic_auth, token_auth

@bp.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    """
    Generate a new token for the authenticated user.

    Returns:
        dict: A dictionary containing the new token.
    """
    token = basic_auth.current_user().get_token()
    db.session.commit()
    return {'token': token}

@bp.route('/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    """
    Revoke the current user's token.

    Returns:
        tuple: An empty string and the HTTP status code 204 (No Content).
    """
    token_auth.current_user().revoke_token()
    db.session.commit()
    return '', 204