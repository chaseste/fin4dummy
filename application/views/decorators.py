"""Application decorators."""
from functools import wraps

from ..internal.redirects import Redirects

def not_logged_in(f):
    """
    Decorate routes to require a user hasn't logged in
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return Redirects.not_logged_in(lambda : f(*args, **kwargs))
    return decorated_function

def unverified(f):
    """
    Decorate routes to require a user hasn't been verified
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return Redirects.unverified(lambda : f(*args, **kwargs))
    return decorated_function

def unauthenticated(f):
    """
    Decorate routes to require a user hasn't been authenticated
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return Redirects.unauthenticated(lambda : f(*args, **kwargs))
    return decorated_function

def authenticated(f):
    """
    Decorate routes to require authentication.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return Redirects.authenticated(lambda : f(*args, **kwargs))
    return decorated_function
