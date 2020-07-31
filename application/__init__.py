"""Initialize application."""
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from dictalchemy import make_class_dictable

from flask import Flask, request, session, render_template
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_bootstrap import Bootstrap
from flask_fontawesome import FontAwesome
from flask_mobility import Mobility
from flask_jwt_extended import JWTManager

from .internal.redirects import Redirects
from .internal.filters import usd, capitalize
from .internal.emails import Emails
from .internal.stocks import Stocks
from .internal.otps import OTPs
from .internal.tokens import URLTokens
from .internal.sms import SMSs
from .internal.geolocations import GeoLocations
from .views.templates import BaseTemplates as _templates

db = SQLAlchemy()
csrf = CSRFProtect()
mail = Emails()
stock = Stocks()
otp = OTPs()
token = URLTokens()
sms = SMSs()
geo = GeoLocations()

def create_app():	
	app = Flask(__name__)
	app.config.from_pyfile('config.py')

	app.jinja_env.filters["usd"] = usd
	app.jinja_env.filters["capitalize"] = capitalize

	csrf.init_app(app)
	
	db.app = app
	db.init_app(app)	
	with app.app_context():
		make_class_dictable(db.Model)
		from . import models
	
	Migrate(app, db)
	Session(app)
	Bootstrap(app)
	FontAwesome(app)
	Mobility(app)
	JWTManager(app)

	def errorhandler(e):
		"""Handle error"""
		if isinstance(e, CSRFError):
			return Redirects.login(True)

		if not isinstance(e, HTTPException):
			e = InternalServerError()
		return _templates.apology(e.name, e.code)
	
	for code in default_exceptions:
		app.errorhandler(code)(errorhandler)

	mail.init(app)
	stock.init(app)
	token.init(app)
	sms.init(app)
	geo.init(app)

	with app.app_context():
		from .views import auths, accounts, portfolios
		from .apis import markets, portfolios, tokens

	@app.after_request
	def after_request(response):
		"""Ensure responses aren't cached"""
		response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
		response.headers["Expires"] = 0
		response.headers["Pragma"] = "no-cache"
		return response

	return app
