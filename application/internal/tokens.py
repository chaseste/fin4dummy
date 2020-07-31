""" Applicaton Tokens """
from datetime import timedelta
from typing import Optional
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity

class JWTTokens:
    @staticmethod
    def access(user_id: int = None, expires: timedelta = None):
        return create_access_token(identity=user_id or get_jwt_identity(), expires_delta=expires)

    @staticmethod
    def refresh(user_id: int, expires: timedelta = None):
        return create_refresh_token(identity=user_id, expires_delta=expires)

class URLTokenExpired(Exception):
    """ Indicates the token as expired """
    pass

class URLTokens:
    """ URL Safe Tokens """

    def __init__(self, app=None):
        if app is not None:
            self.init(app)

    def init(self, app) -> None:
        self.secret_key = app.config["SECRET_KEY"]
        self.age = app.config["TOKEN_AGE"]

    def __serializer(self) -> URLSafeTimedSerializer:
        return URLSafeTimedSerializer(self.secret_key)

    def generate(self, val) -> str:
        """ Generates a secure token for the value """ 
        return self.__serializer().dumps(val, salt="finance-tokens")

    def val(self, token: str) -> Optional:
        """ Extracts the value from the supplied token """
        try:        
            return self.__serializer().loads(token, salt="finance-tokens", max_age=self.age)
        except SignatureExpired:
            raise URLTokenExpired()
