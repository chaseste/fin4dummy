"""Data models."""
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship

from .internal.dates import Dates

from . import db

class Users(db.Model):
	"""Data model for user accounts."""

	__tablename__ = 'users'

	id = db.Column(db.Integer, index=True, primary_key=True, autoincrement=True)
	username = db.Column(db.String(64), index=True, unique=True, nullable=False)
	first_name = db.Column(db.String(50), index=False, unique=False, nullable=False)
	last_name = db.Column(db.String(50), index=False, unique=False, nullable=False)
	email = db.Column(db.String(320), index=False, unique=False, nullable=False)
	hash = db.Column(db.Text, index=False, unique=False, nullable=False)
	cash = db.Column(db.Float(precision='12,2'), index=False, unique=False, nullable=False, default=10000)
	verify_ind = db.Column(db.SmallInteger, nullable=False, default=0)
	verify_dt_tm = db.Column(db.Text, index=False, unique=False, nullable=True)
	locked_ind = db.Column(db.SmallInteger, nullable=False, default=0)
	balances = relationship("Balances")
	holdings = relationship("Holdings")
	closed_positions = relationship("ClosedPositions")
	history = relationship("Transacted")
	twofa = relationship("TwoFactorAuth")
	locs = relationship("UserLocations")

	def __init__(self, username, first, last, email, password, verified):
		self.username = username.lower()
		self.first_name = first.lower()
		self.last_name = last.lower()
		self.email = email
		self.password = password
		self.verified = verified

	@property
	def locked(self):
		return self.locked_ind == 1

	@property
	def verified(self):
		return self.verify_ind == 1

	@property
	def password(self):
		raise AttributeError('password is not readable')

	@locked.setter
	def locked(self, locked):
		self.locked_ind = 1 if locked else 0

	@verified.setter
	def verified(self, verified):
		self.verify_ind = 1 if verified else 0
		if verified:
			self.verify_dt_tm = Dates.now_utc_str()

	@password.setter
	def password(self, password):
		self.hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.hash, password)

	def __repr__(self):
		return "<User(id='{0}', username='{1}', verified='{2}', locked='{3}', cash='{4}')>".format(
			self.id, self.username, self.verified, self.locked, self.cash)

class UserLocations(db.Model):
	"""Data model for user access locations."""

	__tablename__ = 'user_locations'

	id = db.Column(db.Integer, index=True, primary_key=True, autoincrement=True)
	user_id = db.Column(db.ForeignKey('users.id'), index=True, unique=False, nullable=False)
	city = db.Column(db.String(50), index=False, unique=False, nullable=False)
	region = db.Column(db.String(35), index=False, unique=False, nullable=False)
	country = db.Column(db.String(100), index=False, unique=False, nullable=False)
	loc = db.Column(db.String(100), index=False, unique=False, nullable=False)

	def __init__(self, user_id, details):
		self.user_id = user_id
		self.city = details["city"]
		self.region = details["region"]
		self.country = details["country"]
		self.loc = details["loc"]

	def __repr__(self):
		return "<Location(id='{0}', user_id='{1}', city='{2}', region='{3}', country='{4}', loc='{5}')>".format(
			self.id, self.user_id, self.city, self.region, self.loc)

class TwoFactorAuth(db.Model):
	"""Data model for two factor authentication (2fa)."""

	__tablename__ = 'two_factor_auth'

	id = db.Column(db.Integer, index=True, primary_key=True, autoincrement=True)
	user_id = db.Column(db.ForeignKey('users.id'), index=True, unique=False, nullable=False)
	auth_flag = db.Column(db.SmallInteger, nullable=False, default=1)

	def __init__(self, user_id, enabled):
		self.user_id = user_id
		self.enabled = enabled

	@property
	def enabled(self):
		return self.auth_flag == 1

	@enabled.setter
	def enabled(self, enabled):
		self.auth_flag = 1 if enabled else 0

	def __repr__(self):
		return "<TwoFactorAuth(id='{0}', user_id='{1}', auth_flag='{2}')>".format(
			self.id, self.user_id, self.auth_flag)

class Balances(db.Model):
	"""Data model for user account balances."""

	__tablename__ = 'balances'

	id = db.Column(db.Integer, index=True, primary_key=True, autoincrement=True)
	user_id = db.Column(db.ForeignKey('users.id'), index=True, unique=False, nullable=False)
	value = db.Column(db.Float(precision='12,2'), index=False, unique=False, nullable=False)
	bal_dt_tm = db.Column(db.Text, index=False, unique=False, nullable=False)

	def __repr__(self):
		return "<Balance(id='{0}', user_id='{1}', value='{2}')>".format(
			self.id, self.user_id, self.value)

class Holdings(db.Model):
	"""Data model for user holdings."""

	__tablename__ = 'holdings'
	id = db.Column(db.Integer, index=True, primary_key=True, autoincrement=True)
	user_id = db.Column(db.ForeignKey('users.id'), index=True, unique=False, nullable=False)
	symbol = db.Column(db.String(6), index=False, unique=False, nullable=False)
	shares = db.Column(db.Integer, index=False, unique=False, nullable=False)
	price = db.Column(db.Float(precision='12,2'), index=False, unique=False, nullable=False)
	
	def __repr__(self):
		return "<Holding(id='{0}', user_id='{1}', symbol='{2}', shares='{3}', price='{4}')>".format(
			self.id, self.user_id, self.symbol, self.shares, self.price)

class ClosedPositions(db.Model):
	"""Data model for closed user positions."""

	__tablename__ = 'closed_positions'
	id = db.Column(db.Integer, index=True, primary_key=True, autoincrement=True)
	user_id = db.Column(db.ForeignKey('users.id'), index=True, unique=False, nullable=False)
	symbol = db.Column(db.String(6), index=False, unique=False, nullable=False)
	shares = db.Column(db.Integer, index=False, unique=False, nullable=False)
	pps = db.Column(db.Float(precision='12,2'), index=False, unique=False, nullable=False)
	price = db.Column(db.Float(precision='12,2'), index=False, unique=False, nullable=False)
	close_dt_tm = db.Column(db.Text, index=False, unique=False, nullable=False)

	def __repr__(self):
		return "<ClosedPosition(id='{0}', user_id='{1}', symbol='{2}', shares='{3}', pps='{4}', price='{5}', close_dt_tm='{6}')>".format(
			self.id, self.user_id, self.symbol, self.shares, self.pps, self.price, self.close_dt_tm)

class Transacted(db.Model):
	"""Data model for user transactions."""

	__tablename__ = 'transacted'
	id = db.Column(db.Integer, index=True, primary_key=True, autoincrement=True)
	type = db.Column(db.String(5), index=False, unique=False, nullable=False)
	user_id = db.Column(db.ForeignKey('users.id'), index=True, unique=False, nullable=False)
	name = db.Column(db.Text, index=False, unique=False, nullable=False)
	symbol = db.Column(db.String(6), index=False, unique=False, nullable=False)
	shares = db.Column(db.Integer, index=False, unique=False, nullable=False)
	price = db.Column(db.Float(precision='12,2'), index=False, unique=False, nullable=False)
	cost = db.Column(db.Float(precision='12,2'), index=False, unique=False, nullable=False)
	trans_dt_tm = db.Column(db.Text, index=False, unique=False, nullable=False)
	
	def __repr__(self):
		return "<Transacted(id='{0}', user_id='{1}', type='{2}', symbol='{3}', shares='{4}', price='{5}', cost='{6}', trans_dt_tm='{7}')>".format(
			self.id, self.user_id, self.type, self.symbol, self.shares, self.price, self.cost, self.trans_dt_tm)
