"""Flask entry point

Command:
flask run

Configs:
Flask loads the .env and .flaskenv for you. No additional code is 
needed aside from calling the factory method. See application/config.py
for more information

Notes:
Flask will automatically find the wsgi.py and app.py entry points
"""
from application import create_app


app = create_app()
