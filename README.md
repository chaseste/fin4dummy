# Finance
Simple [finance](https://www.fin4dummy.com) application built in python using Flask

## Why?
This project was inspired by [C$50 Finance](https://cs50.harvard.edu/x/2020/tracks/web/finance/). The intent was to take the basic project and extend it. 

### Enhancements
- [WTForms](https://wtforms.readthedocs.io/en/2.3.x/)
- [CSRF Protection](https://flask-wtf.readthedocs.io/en/stable/csrf.html)
- [Mobile Friendly](https://flask-mobility.readthedocs.io/en/latest/)
- [Sqlalchemy ORM](https://docs.sqlalchemy.org/en/13/orm/)
- [Database Migrations](https://flask-migrate.readthedocs.io/en/latest/)
- [MySql Integration](https://pypi.org/project/mysql-connector-python/)
- [Sending SMS](https://pypi.org/project/twilio/)
- [OTP / verification codes](https://pypi.org/project/pyotp/)
- [JWT Tokens](https://flask-jwt-extended.readthedocs.io/en/stable/)
- Rest APIs
- Client side rendering (javascript/rest service integration)
- Sending Emails
- Account Verification
- Account Management
- 2fa (Email | SMS)
- Limit password attempts / Lockout user
- Geolocation / Suspicious location identification
- Password resets / Username recovery
- Deployment / Hosting

# Setup
- Install python (if not already installed)
- Run pip install
> pip install -r requirements.txt
- Register with IEX
- Register with ipinfo
- Add .env file with appropriate configurations to the root directory
- Install waitress (if not already installed)
> pip install waitress

# Development
## Flasks development server
- Execute Flask
> flask run
- Access the applicaition on localhost:8080
## Waitress 
- Execute the run.py script
> waitress-serve --call run:run_app
- Access the applicaition on localhost:8080

# Environments
Flask's development server will automatically load the .flaskenv and .env files. To simplify configuration the application will load the following configurations from the .env file.

## .env 
```
#.env
# Sample environment variables

##########################
#   SMTP Email Settings
##########################
SMPT_PORT=465
SMPT_SENDER_PWD=YOUR_PASSWORD
SMPT_HOST=YOUR_HOST
SMPT_SENDER=YOUR_EMAIL
SMPT_SENDER_FROM=YOUR_EMAIL

#############
#   SMS
#############
TWILIO_SID=YOUR_SID
TWILIO_TOKEN=YOUR_TOKEN
TWILIO_NUMBER=YOUR_NUMBER

#############
#   CSRF
#############
SECRET_KEY=YOUR_KEY

#############
#   JWT
#############
JWT_SECRET_KEY=YOUR_KEY

#############
#   IEX
#############
IEX_API_KEY=YOUR_KEY

#############
#   IPINFO
#############
IPINFO_TOKEN=YOUR_TOKEN

#############
#   Tokens
#############
TOKEN_AGE=3600

#############
# SQLALCHEMY
#############
SQLALCHEMY_ECHO=False

#Sqllite
#SQLALCHEMY_DATABASE_URI=sqlite:///../finance.db

# MySql
SQLALCHEMY_DATABASE_URI=mysql+mysqlconnector://<user>:<password>@<host>/<schema>
```

## Waitress
[Waitress](https://pypi.org/project/waitress/) is used to run the application locally on a production WSGI server. Waitress doesn't load the .env file. The run script does this for you.

# IEX APIs
Finance makes use of the free APIs [IEX](iexcloud.io/) provides. You'll need to create an account to get a KEY to access them.

- Visit iexcloud.io/cloud-login#/register/.
- Enter your email address and a password, and click “Create account”.
- On the next page, scroll down to choose the Start (free) plan.
- Once you’ve confirmed your account via a confirmation email, sign in to iexcloud.io.
- Click API Tokens.
- Copy the key that appears under the Token column (it should begin with pk_).
- Add to .env file.

# Databases
Finance has been tested with both sqllite (dev) and mysql (prod). The mysql connecter is included for you.

## Development
### MySql
- Install docker (if not already installed)
- Install MySql Workbench (if not already installed)
- Create MySql container
```
docker container create -p 3306:3306 --name mysql-latest ^
-e MYSQL_ROOT_PASSWORD=root ^
-e MYSQL_USER=root ^
-e MYSQL_PASSWORD=root ^
-e MYSQL_DATABASE=finance ^
mysql/mysql-server:latest ^
mysqld --lower_case_table_names=1 --skip-ssl --disable-ssl --ssl=0 --character_set_server=utf8mb4 --explicit_defaults_for_timestamp
```
- Start the container
> docker start mysql-latest
- Verify the container is running
> docker ps
- Access the database with MySql Workbench to verify everything is working correctly
> On the SSL tab specify No for Use SSL

### Verify Users
- Log into the MySql container to verify user credentials
> docker exec -it mysql-latest mysql -uroot -p
- Enter password of "root"
- Query the users
> select user from mysql.user;

### Create User / Modify Privledges
- Log into the MySql container to verify user credentials
> docker exec -it mysql-latest mysql -uroot -p
- Enter password of "root"
- Create the user
```
create user 'someuser'@'localhost' identified by 'somepassword'
grant all privileges on *.* to 'someuser'@'localhost' with grant option;
flush privileges;
```

# Production
## Pythonanywhere
- Register for a free account
- Setup MySql database
- Add a web app using the manual configuration
> The Flask wizard is meant to create a simple app with minimal effort
- Open a console and check out the project
> git clone https://github.com/chasestew/finance.git
- Open the finance directory
- Add the .env file along with these variables. See [documentation](https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/) for the configurations.
```
SQLALCHEMY_POOL_RECYCLE=9
SQLALCHEMY_POOL_TIMEOUT=9
```
- Create virtual environment
> mkvirtualenv myvirtualenv --python=/usr/bin/python3.8
- Exit the virtual environment
> deactivate
- Install requirements (Make sure to include the --user along with pip3 for python 3)
```
 workon myvirtualenv
 pip3 install -r requirement.txt
 deactivate
 ```
- Setup the database
```
/home/<user>/.virtualenvs/myvirtualenv/bin/python /home/<user>/finance/manage.py db upgrade
```
- Create the finadmin account. Should use a password you'll remember
```
/home/<user>/.virtualenvs/myvirtualenv/bin/python /home/<user>/finance/manage.py create_admin "<password>"
```
- Configure the virtual environment in the web app setup
> /home/user_replace/.virtualenvs/myvirtualenv/
- Configure the source code directory in the web app setup
> /home/user_replace/finance
- Configure the WSGI config file
```
# Make sure the project is on the path
import sys

project_home = '/home/user_replace/finance'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Load the .env file
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(project_home, '.env'))

# Import the application
from wsgi import app as application
```
- Save the file and reload the application
- Create task for updating the accounts
```
frequency = Daily
time = After hours (something like 20:30 UTC)
command = /home/<user>/.virtualenvs/myvirtualenv/bin/python /home/<user>/finance/manage.py update_accounts
```
