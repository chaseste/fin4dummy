import datetime

from flask import current_app as app, jsonify, request
from flask_jwt_extended import jwt_refresh_token_required

from ..internal.tokens import JWTTokens
from ..manager import BasicAuth
from .. import csrf

def __access_token(user_id: int = None):
    expires = datetime.timedelta(minutes=app.config["API_ACCESS_EXPIRES"])
    return JWTTokens.access(user_id, expires)

def __refresh_token(user_id: int):
    expires = datetime.timedelta(hours=app.config["API_REFRESH_EXPIRES"])
    return JWTTokens.refresh(user_id, expires)

@app.route("/token", methods=["GET", "POST"])
@csrf.exempt
def token():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    try:
        user = BasicAuth.authenticate(username, password)
    except (BasicAuth.BadCredentials, BasicAuth.AccountLocked):
        return jsonify({"msg": "Bad username or password"}), 400

    if not user.verified:
        return jsonify({"msg": "Account must be verified before accessing APIs"}), 400
    tokens = {
        'access_token': __access_token(user.id),
        'refresh_token': __refresh_token(user.id)
    }
    return jsonify(tokens), 200

@app.route('/token/refresh', methods=['POST'])
@jwt_refresh_token_required
@csrf.exempt
def refresh():
    token = {
        'access_token': __access_token()
    }
    return jsonify(token), 200
