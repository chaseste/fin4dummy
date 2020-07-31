""" Application urls"""
from flask import url_for

class URLs:
    @staticmethod
    def history_url(page_num: int):
        return url_for("history", page=page_num)

    @staticmethod
    def verify_email_url(token: str, external: bool =True):
        return url_for("verify_email", token=token, _external=external)

    @staticmethod
    def change_password_url(token: str, external: bool =True):
        return url_for("change_password", token=token, _external=external)
