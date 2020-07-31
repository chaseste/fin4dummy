""" Application registration / authentication routes."""
from datetime import datetime

from flask import flash, request, session
from flask import current_app as app

from ..internal.tokens import JWTTokens
from ..internal.redirects import Redirects
from ..manager import Registrar, BasicAuth, TwoFactAuth, AccountManager, UserContext

from .decorators import unverified, unauthenticated, not_logged_in
from .forms import AuthForms as _forms
from .templates import AuthTemplates as _templates

@app.route("/register", methods=["GET", "POST"])
@not_logged_in
def register():
	""" Register a user in the system. The username, and email must be unique """
	form = _forms.register(request)
	if request.method == "POST" and form.validate_on_submit():
		try:
			Registrar.register(form.username.data, form.first.data, form.last.data, 
				form.email.data, form.password.data)
			flash("A confirmation email has been sent to your email address.", "success")
			return Redirects.home()
		except Registrar.UserAlreadyRegistered:
			flash('User alreaded registered!', "error")
	return _templates.register(form)

@app.route("/login", methods=["GET", "POST"])
@not_logged_in
def login():
	""" Log user in. Depending on their registration / authenication configs the user 
		will be directed to the appopriate place to either complete their verification
		process or authenicate / prove its them """	
	form = _forms.login(request)
	if request.method == "POST" and form.validate_on_submit():
		try:
			user = BasicAuth.authenticate(form.username.data, form.password.data)

			prev_url = session.get("prev_url")
			session.clear()
			
			session["prev_url"] = prev_url
			session["user_id"] = user.id
			session["jwt"] = JWTTokens.access(user.id)
			session["login_dt_tm"] = datetime.utcnow()
			
			if not user.verified:
				return Redirects.confirm_email()
			session["user_verified"] = True
			
			if not AccountManager.two_fa_enabled():
				session["user_auth"] = True
				return Redirects.home()
			return Redirects.send_otp()
		except (BasicAuth.BadCredentials, BasicAuth.AccountLocked) as e:
			if isinstance(e, BasicAuth.BadCredentials):
				flash("Invalid username or password.", "error")
			else:
				flash("Account locked. Please reset your password via forgot my password.", "error")
	return _templates.login(form)

@app.route("/logout")
def logout():
	""" Logs the user out """
	session.clear()
	return Redirects.home()

@app.route("/verify-email", methods=["GET"])
@unverified
def verify_email():
	""" Verifies the email. If the user has logged in, they will be automatically logged out to 
		start the authentication process"""
	session.clear() 
	try:
		user = Registrar.verify(request.args.get("token", default=""))
	except Registrar.BadVerification as e:
		if isinstance(e, Registrar.VerificationExpired):
			flash('The verification link has expired. Please log in to verify your account.', "error")
		return Redirects.login()
	
	flash('Account verified.', "success")
	return _templates.email_confirmed(user)

@app.route("/confirm-email", methods=["GET"])
@unverified
@unauthenticated
def confirmation_email():
	""" Requests the user to confirm their email before they can access the rest of the site """	
	return _templates.confirm_email(UserContext.user())

@app.route("/resend-email-verification", methods=["GET"])
@unverified
@unauthenticated
def resend_email_verification():
	""" Resends the user's verification email in the event they didn't get it or the link expired """
	if Registrar.request_verification():
		flash('Verification email resent.', "success")
	return Redirects.confirm_email()

@app.route("/send-otp", methods=["GET", "POST"])
@unauthenticated
def send_otp():
	""" Request the user to authenticate themselves using a OTP """	
	user = UserContext.user()
	form = _forms.send_otp(request)
	if request.method == "POST" and form.validate_on_submit():
		return Redirects.verify_otp("sms", TwoFactAuth.request_verification(user, "sms", form.phone.data))
	elif request.method == "GET" and request.args.get("method", default="") == "mail":
		return Redirects.verify_otp("mail", TwoFactAuth.request_verification(user, "mail", user.email))
	return _templates.send_otp(form)

@app.route("/resend-otp", methods=["GET"])
@unauthenticated
def resend_otp():
	""" Resend the user's otp """
	method = request.args.get("method", default="")
	dest = request.args.get("dest", default="")
	try:
		TwoFactAuth.request_again(method, dest)
		flash('OTP resent.', "success")
		return Redirects.verify_otp(method, dest)
	except Exception:
		return Redirects.send_otp()
	
@app.route("/verify-otp", methods=["GET", "POST"])
@unauthenticated
def verify_otp():
	""" Verify the OTP provided by the user matches the one sent to them """
	method = request.args.get("method", default="")
	dest = request.args.get("dest", default="")
	form = _forms.verify_otp(request)
	if request.method == "POST" and form.validate_on_submit():
		try:
			TwoFactAuth.verify(method, dest, form.otp.data)
			session["user_auth"] = True
			return Redirects.home()
		except Exception as e:
			if not isinstance(e, TwoFactAuth.BadOTP):
				return Redirects.send_otp()
			flash('Invalid otp.', "error")
	return _templates.verify_otp(form, method, dest)
