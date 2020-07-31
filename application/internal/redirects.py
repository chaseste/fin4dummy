from flask import redirect, url_for, request
from flask import session

from .urls import URLs

class Redirects:
    """ Application redirects """

    @classmethod
    def not_logged_in(cls, protected):
        """ Ensures a user has not logged in. If they have, they'll be
            redirected home """
        if not session.get("user_id") is None:
            return cls.home()
        return protected()

    @classmethod
    def unverified(cls, protected):
        """ Ensures the user hasn't been verified if one is in context. 
            In the event a user is in context, we'll redirect them home if they 
            have been authenticated in another window, otherwise if they have been 
            verified we'll simply log them out to force them to log back in to 
            start the authentication process """
        if not session.get("user_id") is None:
            if not session.get("user_auth") is None:
                return cls.home()
            elif not session.get("user_verified") is None:
                return cls.logout()
        return protected()

    @classmethod
    def unauthenticated(cls, protected):
        """ Ensures a user is 1) in context and 2) hasn't been authenticated """
        if session.get("user_id") is None:
            return cls.login(True)
        elif not session.get("user_auth") is None:
            return cls.home()
        return protected()

    @classmethod
    def authenticated(cls, protected, default=lambda : Redirects.login(True)):
        """ Ensures a user is 1) in context and 2) has been verified and 3) has been authenticated """
        if session.get("user_id") is None:
            return default()
        elif session.get("user_verified") is None:
            return cls.confirm_email()
        elif session.get("user_auth") is None:
            return cls.send_otp()
        return protected()

    @staticmethod
    def login(_redirect=False):
        if _redirect:
            prev_url = request.path
            if prev_url != "/login":
                session["prev_url"] = request.path
        return redirect("/login")

    @staticmethod
    def logout():
        return redirect("/logout")

    @staticmethod
    def home():
        prev_url = session.get("prev_url")
        if not prev_url is None:
            session["prev_url"] = None
            return redirect(prev_url)
        return redirect("/")

    @staticmethod
    def send_otp():
        return redirect("/send-otp")

    @staticmethod
    def verify_otp(method: str, dest: str):
        return redirect(f"/verify-otp?method={method}&dest={dest}")

    @staticmethod
    def account():
        return redirect("/account")

    @staticmethod
    def confirm_email():
        return redirect("/confirm-email")

    @staticmethod
    def update_password(token: str):
        return redirect(URLs.change_password_url(token, False))
