""" Application View templates"""
from flask import render_template, request

from ..internal.urls import URLs
from ..internal.utils import escape

from .forms import LoginForm

class BaseTemplates:
    @classmethod
    def template(cls, name, **kwargs):
        dir = cls.__dict__["__dir__"] if "__dir__" in cls.__dict__ else "" 
        return render_template("".join([dir, name]), desktop=not getattr(request, "MOBILE", False), **kwargs)

    @classmethod
    def form(cls, _template, form, **kwargs):
        return cls.template(_template, form=form, template='form-template', **kwargs)

    @staticmethod
    def apology(message: str, code: int = 400):
        return render_template("apology.html", top=code, bottom=escape(message)), code

class AuthTemplates(BaseTemplates):
    __dir__ = "/auth/"

    @classmethod
    def register(cls, form):
        return cls.form("register.html", form)

    @classmethod
    def confirm_email(cls, user):
        return cls.template("confirm_email.html", first=user.first_name)

    @classmethod
    def email_confirmed(cls, user):
        return cls.template("email_confirmed.html", first=user.first_name)

    @classmethod
    def login(cls, form=None):
        form = form or LoginForm()
        return cls.form("login.html", form)

    @classmethod
    def send_otp(cls, form):
        return cls.form("send_otp.html", form)

    @classmethod
    def verify_otp(cls, form, method, dest):
        return cls.form("verify_otp.html", form, method=method, dest=dest)

class AccountTemplates(BaseTemplates):
    __dir__ = "/account/"

    @classmethod
    def account(cls, user):
        return cls.template("account.html", user=user)

    @classmethod
    def change_email(cls, form):
        return cls.form("change_email.html", form)

    @classmethod
    def change_password(cls, form, token):
        return cls.form("change_password.html", form, token=token)

    @classmethod
    def deposit(cls, form):
        return cls.form("deposit.html", form)

    @classmethod
    def forgot_username(cls, form):
        return cls.form("forgot_username.html", form)

    @classmethod
    def password_reset(cls, form):
        return cls.form("password_reset.html", form)

    @classmethod
    def twofa(cls, form):
        return cls.form("2fa.html", form)

class PortfolioTemplates(BaseTemplates):
    @classmethod
    def index(cls):
        return cls.template("index.html")

    @classmethod
    def insights(cls, insights):
        return cls.template("insights.html", values=insights["values"], labels=insights["labels"], 
            active=insights["active"], gainers=insights["gainers"], losers=insights["losers"])

    @classmethod
    def portfolio(cls, portfolio):
        return cls.template("portfolio.html", positions=portfolio["positions"], cost=portfolio["cost"], 
            change=portfolio["change"], value=portfolio["value"], closed_positions=portfolio["closed_positions"])

    @classmethod
    def closed_positions(cls, closed_positions):
        return cls.template("closed_positions.html", positions=closed_positions["positions"], 
            cost=closed_positions["cost"], change=closed_positions["change"], value=closed_positions["value"])

    @classmethod
    def position(cls, position):
        return cls.template("position.html", position=position)

    @classmethod
    def buy(cls, form):
        return cls.form("buy.html", form)

    @classmethod
    def history(cls, transactions):
        next_url = None
        if transactions.has_next:
            next_url = URLs.history_url(transactions.next_num)

        prev_url = None
        if transactions.has_prev:
            prev_url = URLs.history_url(transactions.prev_num)

        return cls.template("history.html", transactions=transactions.items, 
            next_url=next_url, prev_url=prev_url)

    @classmethod
    def quote(cls, form):
        return cls.form("quote.html", form)

    @classmethod
    def quoted(cls, quote):
        return cls.template("quoted.html", qoute=quote["ticker"], headlines=quote["headlines"], 
            share_holder=quote["share_holder"])

    @classmethod
    def sell(cls, form):
        return cls.form("sell.html", form)
