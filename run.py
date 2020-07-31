"""Waitress entry point

waitress-serve --call run:run_app

Configs:
Waitress requires the .env file to be loaded explicity. 
See application/config.py for more information.

Notes:
Waitress uses port 8080 by default
"""
from dotenv import load_dotenv

from application import create_app

def run_app():
	load_dotenv('.env')

	app = create_app()
	return app
