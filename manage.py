"""Flask shell script"""
import sys
import os

from dotenv import load_dotenv
from flask_script import Manager
from flask_migrate import MigrateCommand

from application.internal.dates import Dates
from application.manager import Registrar, AccountManager
from application import create_app

load_dotenv(os.path.join(sys.path[0], '.env'))
manager = Manager(create_app())
manager.add_command('db', MigrateCommand)

@manager.command
def create_admin(password, reset="false"):
    """Creates the admin account"""        
    try:
        admin = Registrar.query_by_username("finadmin")
        if admin is None:
            print("Creating admin account....")
        else:
            if reset.lower() != "true":
                print("Admin account already exists.")
                return        
            
            print("Reseting admin account....")
            Registrar.unregister(admin.id)

        Registrar.register("finadmin", "Admin", "Admin", "admin@fin4dummy.com", 
            password, True, False, False)
        print("Complete.")
    except Exception as e:
        print(" ".join(["Error occurred while creating admin account: \n", str(e)]))
        db.session.rollback()

@manager.command
def update_accounts(force="false"):
    """Updates the accounts"""
    if force.lower() != "true" and not Dates.is_week_day():
        print("Accounts aren't updated on the weekend.")
        return

    try:
        print("Updating accounts....")
        AccountManager.update_balances()
        print("Complete.")
    except Exception as e:
        print(" ".join(["Error occurred while updating accounts: \n", str(e)]))
        db.session.rollback()

if __name__ == "__main__":
    manager.run()
