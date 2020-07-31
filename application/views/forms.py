"""Application Form."""
import phonenumbers

from flask import request
from flask_wtf import FlaskForm

from wtforms import SelectField, StringField, RadioField, IntegerField, FloatField, SubmitField, PasswordField, ValidationError
from wtforms.validators import DataRequired, Length, EqualTo, NumberRange, Email
from wtforms.fields.html5 import EmailField

class NotEqualTo:
	"""
	Compares the values of two fields.
	:param fieldname:
		The name of the other field to compare to.
	:param message:
		Error message to raise in case of a validation error. Can be
		interpolated with `%(other_label)s` and `%(other_name)s` to provide a
		more helpful error.
	"""
	
	def __init__(self, fieldname, message=None):
		self.fieldname = fieldname
		self.message = message

	def __call__(self, form, field):
		try:
			other = form[self.fieldname]
		except KeyError:
			raise ValidationError(
				field.gettext("Invalid field name '%s'.") % self.fieldname
			)
		if field.data == other.data:
			d = {
				"other_label": hasattr(other, "label")
				and other.label.text
				or self.fieldname,
				"other_name": self.fieldname,
			}
			message = self.message
			if message is None:
				message = field.gettext("Field must not be equal to %(other_name)s.")

			raise ValidationError(message % d)

class LessThanOrEqualTo:
	"""
	Compares the values of two fields.
	:param fieldname:
		The name of the other field to compare to.
	:param message:
		Error message to raise in case of a validation error. Can be
		interpolated with `%(other_label)s` and `%(other_name)s` to provide a
		more helpful error.
	"""
	
	def __init__(self, fieldname, message=None):
		self.fieldname = fieldname
		self.message = message

	def __call__(self, form, field):
		self.fieldname
		try:
			other = form[self.fieldname]
		except KeyError:
			raise ValidationError(
				field.gettext("Invalid field name '%s'.") % self.fieldname
			)
		if field.data > other.data:
			d = {
				"other_label": hasattr(other, "label")
				and other.label.text
				or self.fieldname,
				"other_name": self.fieldname,
			}
			message = self.message
			if message is None:
				message = field.gettext("Field must not be equal to %(other_name)s.")

			raise ValidationError(message % d)

class PhoneNumber:
	"""
	Ensures the field is a valid phone number.
	:param message:
		Error message to raise in case of a validation error.
	"""
	
	def __call__(self, form, field):
		try:
			parsed = phonenumbers.parse(field.data)
			if not phonenumbers.is_valid_number(parsed):
				raise ValidationError('Invalid phone number.')	
		except phonenumbers.NumberParseException as e:
			raise ValidationError(str(e))

class LoginForm(FlaskForm):
	username = StringField("Username", [DataRequired(), Length(min=4, message="Username is too short.")])
	password = PasswordField("Password", [DataRequired(), Length(min=4, message="Password is too short.")])
	submit = SubmitField()

class QuoteForm(FlaskForm):
	symbol = StringField("Symbol", [DataRequired(), Length(max=5, message="Symbol is too long.")])
	submit = SubmitField()

class BuyForm(FlaskForm):
	symbol = StringField("Symbol", [DataRequired(), Length(max=5, message="Symbol is too long.")])
	price = StringField("Price")
	cash = StringField("Cash")
	shares = IntegerField("Shares", [DataRequired(message="Invalid quantity."),
						  NumberRange(min=1, message="Invalid quantity.")])
	submit = SubmitField()

	def __init__(self, form):
		super().__init__(form)

		if request.method == "GET":
			from ..manager import PortfolioManager

			symbol = request.args.get("symbol", default = "")
			if symbol != "":
				self.symbol.data = symbol
				self.price.data = PortfolioManager.asking_price(symbol)
				self.shares.data = 1
			self.cash.data = PortfolioManager.cash_on_hand()

class SellForm(FlaskForm):
	symbol = SelectField("Symbol", coerce=int)
	price = StringField("Price")
	pps = StringField("PPS")
	holding = IntegerField("Holding", [DataRequired()])
	shares = IntegerField("Shares", [DataRequired(message="Invalid quantity."),
						  LessThanOrEqualTo("holding", message="Shares exceed holding."),
						  NumberRange(min=1, message="Invalid quantity.")])
	submit = SubmitField()

	def __init__(self, form):
		super().__init__(form)

		from ..manager import PortfolioManager
		self.holdings = PortfolioManager.query_holdings_by_user()
		self.symbol.choices = [(holding.id, holding.symbol) for holding in self.holdings]

		if request.method == "GET":
			holding = self.holdings.first()
			if holding:
				symbol = request.args.get("symbol", default = "")
				if symbol != "":
					holding = list(filter(lambda holding: holding.symbol == symbol, self.holdings))[0]

				self.symbol.data = holding.id
				self.holding.data = holding.shares
				self.price.data = PortfolioManager.asking_price(holding.symbol)
				self.pps.data = holding.price
				self.shares.data = 1
	
	def __holding_for_symbol(self, symbol):
		return 

	def selected_holding(self):
		return list(filter(lambda holding: holding.id == self.symbol.data, self.holdings))[0]

class RegisterForm(FlaskForm):
	first = StringField("First Name", [DataRequired(), Length(max=50, message="First name has a limit of 50 characters.")])
	last = StringField("Last Name", [DataRequired(), Length(max=50, message="Last name has a limit of 50 characters.")])
	username = StringField("Username", [DataRequired(), Length(min=6, max=64, message="Username must be between 6 and 64 characters."),
						   NotEqualTo("password", message="Username/Passwords must be different.")])
	email = EmailField('Email address', [DataRequired(), Email()])
	password = PasswordField("Password", [DataRequired(), Length(min=6, max=64, message="Passwords must be between 6 and 64 characters."),
							 EqualTo("confirm", message="Passwords must match.")])
	confirm  = PasswordField("Repeat Password", [DataRequired()])
	submit = SubmitField()

class ForgotUsernameForm(FlaskForm):
	email = EmailField('Email address', [DataRequired(), Email()])
	submit = SubmitField()

class PasswordResetForm(FlaskForm):
	username = StringField("Username", [DataRequired(), Length(min=4, message="Username is too short.")])
	submit = SubmitField()

class SendOTPForm(FlaskForm):
	phone = StringField("Phone", [DataRequired(), PhoneNumber()])
	submit = SubmitField()

class VerifyOTPForm(FlaskForm):
	otp = StringField("OTP", [DataRequired()])
	submit = SubmitField()

class ChangePasswordForm(FlaskForm):
	password = PasswordField("Password", [DataRequired(), Length(min=4, message="Password is too short."), 
							 EqualTo("confirm", message="Passwords must match.")])
	confirm  = PasswordField("Repeat Password", [DataRequired()])
	submit = SubmitField()

class ChangeEmailForm(FlaskForm):
	email = EmailField('Email address', [DataRequired(), Email(), EqualTo("confirm", message="Emails must match.")])
	confirm  = EmailField("Repeat Email", [DataRequired(), Email()])
	submit = SubmitField()

class TwoFactorForm(FlaskForm):
	enabled = RadioField('Enabled', choices=[('True', 'Always\xa0\xa0\xa0'), ('False', 'Disabled')])

	def __init__(self, form):
		super().__init__(form)

		if request.method == "GET":
			from ..manager import AccountManager
			self.enabled.data = str(AccountManager.two_fa_enabled())

	def is_enabled(self):
		return self.enabled.data == "True"

class DepositForm(FlaskForm):
	deposit = SelectField("Deposit", choices=[(1000, '1K'), (5000, '5K'), (10000, '10K'), (20000, '20K')], coerce=int)
	submit = SubmitField()

class AuthForms:
	@staticmethod
	def login(req: request) -> LoginForm:
		return LoginForm(req.form)

	@staticmethod
	def register(req: request) -> RegisterForm:
		return RegisterForm(req.form)

	@staticmethod
	def send_otp(req: request) -> SendOTPForm:
		return SendOTPForm(req.form)

	@staticmethod
	def verify_otp(req: request) -> VerifyOTPForm:
		return VerifyOTPForm(req.form)

class AccountForms:
	@staticmethod
	def forgot_username(req: request) -> ForgotUsernameForm:
		return ForgotUsernameForm(req.form)

	@staticmethod
	def password_reset(req: request) -> PasswordResetForm:
		return PasswordResetForm(req.form)

	@staticmethod
	def change_password(req: request) -> ChangePasswordForm:
		return ChangePasswordForm(req.form)

	@staticmethod
	def change_email(req: request) -> ChangeEmailForm:
		return ChangeEmailForm(req.form)

	@staticmethod
	def two_factor(req: request) -> TwoFactorForm :
		return TwoFactorForm(req.form)
	
	@staticmethod
	def deposit(req: request) -> DepositForm :
		return DepositForm(req.form)

class PortfolioForms:
	@staticmethod
	def quote(req: request) -> QuoteForm:
		return QuoteForm(req.form)

	@staticmethod
	def buy(req: request) -> BuyForm:
		return BuyForm(req.form)

	@staticmethod
	def sell(req: request) -> SellForm:
		return SellForm(req.form)
