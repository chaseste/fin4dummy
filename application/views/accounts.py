""" Application user account routes."""
from flask import flash, request, session
from flask import current_app as app

from ..internal.filters import usd
from ..internal.redirects import Redirects
from ..manager import AccountManager, UserContext

from .decorators import authenticated, not_logged_in
from .forms import AccountForms as _forms
from .templates import AccountTemplates as _templates

@app.route("/forgot-username", methods=["GET", "POST"])
@not_logged_in
def forgot_username():
	"""Forgot Username"""
	form = _forms.forgot_username(request)
	if request.method == "POST" and form.validate_on_submit():
		if AccountManager.forgot_username(form.email.data):
			flash("Email sent. Check your inbox.", "success")
		return Redirects.login()
	return _templates.forgot_username(form)

@app.route("/reset-password", methods=["GET", "POST"])
@not_logged_in
def password_reset():
	"""Password reset"""
	form = _forms.password_reset(request)
	if request.method == "POST" and form.validate_on_submit():
		if AccountManager.forgot_password(form.username.data):
			flash("Email sent. Check your inbox.", "success")
		return Redirects.login()
	return _templates.password_reset(form)

@app.route("/change-password", methods=["GET", "POST"])
def change_password():
	"""Update the user's password"""
	_token = request.args.get("token")
	form = _forms.change_password(request)
	if request.method == "POST" and form.validate_on_submit():
		try:
			if AccountManager.change_password(form.password.data, _token):
				flash("Password updated.", "success")
				return Redirects.authenticated(lambda: Redirects.account(), lambda: Redirects.home())
			else:
				flash("Cannot reuse previous password!", "error")
		except (UserContext.UserNotInContext, AccountManager.ResetPasswordExpired) as e:
			if isinstance(e, AccountManager.ResetPasswordExpired):
				flash('The reset password link has expired. Please request a new one.', "error")
			return Redirects.login()
	return _templates.change_password(form, _token)

@app.route("/account", methods=["GET", "POST"])
@authenticated
def account():
	"""Update the user's account"""
	return _templates.account(UserContext.user())

@app.route("/change-email", methods=["GET", "POST"])
@authenticated
def change_email():
	"""Update the user's email"""
	form = _forms.change_email(request)
	if request.method == "POST" and form.validate_on_submit():
		try:
			AccountManager.change_email(form.email.data)
			flash("Email updated.", "success")
			return Redirects.account()
		except (AccountManager.ReusedEmail, AccountManager.EmailExists) as e:
			if isinstance(e, AccountManager.ReusedEmail):
				flash("Email matches the one on the account!", "error")
			else:
				flash("Email is already registered with an account!", "error")
	return _templates.change_email(form)

@app.route("/2fa", methods=["GET", "POST"])
@authenticated
def twofa():
	"""Update the user's 2fa settings"""
	form = _forms.two_factor(request)
	if request.method == "POST" and form.validate_on_submit():
		enabled = form.is_enabled()
		if AccountManager.two_fa(enabled):
			if enabled:
				flash("Two Factor Auth enabled for account.", "success")
			else:
				flash("Two Factor Auth is disabled for account.", "error")
		return Redirects.account()
	return _templates.twofa(form)

@app.route("/deposit", methods=["GET", "POST"])
@authenticated
def deposit():
	"""Add a deposit to the user's account"""
	form = _forms.deposit(request)
	if request.method == "POST" and form.validate_on_submit():
		AccountManager.deposit(form.deposit.data)
		flash(" ".join(["Deposit of", usd(form.deposit.data), "added to account."]), "success")
		return Redirects.account()
	return _templates.deposit(form)
