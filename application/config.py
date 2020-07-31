"""Application Configuration."""
from os import environ
from tempfile import mkdtemp

def __is_present(name):
	return not environ.get(name) is None

def __required_variable(name):
	if not __is_present(name):
		raise RuntimeError(name)
	return environ.get(name)

def __optional_variable(name, default):
	if not __is_present(name):
		return default
	return environ.get(name)

# IEX API
IEX_API_KEY = __required_variable("IEX_API_KEY")

# IPINFO API
IPINFO_TOKEN = __required_variable("IPINFO_TOKEN")

# Tokens
TOKEN_AGE = int(__required_variable("TOKEN_AGE"))

# SMPT
SMPT_HOST = __required_variable("SMPT_HOST")
SMPT_PORT = __required_variable("SMPT_PORT")
SMPT_SENDER = __required_variable("SMPT_SENDER")
SMPT_SENDER_FROM = __required_variable("SMPT_SENDER_FROM")
SMPT_SENDER_PWD = __required_variable("SMPT_SENDER_PWD")

# SMS / Twilio
TWILIO_SID = __required_variable("TWILIO_SID")
TWILIO_TOKEN = __required_variable("TWILIO_TOKEN")
TWILIO_NUMBER = __required_variable("TWILIO_NUMBER")

# CSRF
SECRET_KEY = __required_variable('SECRET_KEY')

# JWT
JWT_SECRET_KEY = __required_variable('JWT_SECRET_KEY')
JWT_ACCESS_TOKEN_EXPIRES = __optional_variable('JWT_ACCESS_TOKEN_EXPIRES', False)

# API Endpoints
API_ACCESS_EXPIRES = __optional_variable('API_ACCESS_EXPIRES', 30)
API_REFRESH_EXPIRES = __optional_variable('API_REFRESH_EXPIRES', 1)

# Configure DB
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = __required_variable('SQLALCHEMY_DATABASE_URI')

if __is_present("SQLALCHEMY_ECHO"):
	SQLALCHEMY_ECHO = environ.get('SQLALCHEMY_ECHO').lower()  == 'true'

if __is_present("SQLALCHEMY_POOL_RECYCLE"):
	SQLALCHEMY_POOL_RECYCLE = int(environ.get('SQLALCHEMY_POOL_RECYCLE'))

if __is_present("SQLALCHEMY_POOL_TIMEOUT"):
	SQLALCHEMY_POOL_TIMEOUT = int(environ.get('SQLALCHEMY_POOL_TIMEOUT'))

# Ensure templates are auto-reloaded
if __is_present("FLASK_ENV") and environ.get("FLASK_ENV") == "development":
	TEMPLATES_AUTO_RELOAD = True

# Configure session to use filesystem (instead of signed cookies)
SESSION_FILE_DIR = mkdtemp()
SESSION_PERMANENT = False
SESSION_TYPE = "filesystem"
