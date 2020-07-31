""" Application managers """
from flask import session
from flask_jwt_extended import get_jwt_identity

from .internal.stocks import Stocks
from .internal.dates import Dates
from .internal.tokens import URLTokenExpired
from .internal.emails import VerifyMail, OTPMail, UsernameMail, PasswordResetMail, UnrecognizedAccessMail
from .internal.sms import OTPSMS

from .models import Users, Holdings, Balances, TwoFactorAuth, Transacted, ClosedPositions, UserLocations
from . import db, stock, mail, token, otp, sms, geo

class UserContext:
    """ User Context """

    class UserNotInContext(Exception):
        """ Indicates a user is not in context """
        pass

    @classmethod
    def id(cls):
        """ The user.id of the user if one is in context """
        if session.get("user_id") is None:
            user_id = get_jwt_identity()
            if user_id is None:
                raise cls.UserNotInContext()
            return user_id
        return session["user_id"]

    @classmethod
    def user(cls):
        return Users.query.filter_by(id=cls.id()).one()

class Registrar:
    """ User Registrar """
    
    class BadVerification(Exception):
        """ Indicates a bad verification occurred """
        pass

    class VerificationExpired(BadVerification):
        """ Indicates the verification link expired """
        pass

    class UserAlreadyRegistered(Exception):
        """ Indicates a user is already registered """
        pass

    @classmethod
    def register(cls, username, first, last, email, password, verified=False, 
        twofa_enabled=True, send_email=True):
        """ Registers a user in the system """
        if not cls.query_by_username(username) is None:
            raise cls.UserAlreadyRegistered()
        elif not cls.query_by_email(email) is None:
            raise cls.UserAlreadyRegistered()
        user = Users(username, first, last, email, password, verified)
        db.session.add(user)
    
        user = Users.query.filter_by(username=username).one()
        auth = TwoFactorAuth(user.id, twofa_enabled)
        db.session.add(auth)

        db.session.commit()
        if send_email:
            cls.request_verification(user)

    @classmethod
    def request_verification(cls, user=None):
        """ Sends the verification email for the new user """
        user = user or UserContext.user()
        if not user.verified:
            mail.send(VerifyMail(user.email, token.generate(user.email)))
            return True
        return False

    @classmethod
    def verify(cls, _token):
        """ Verifies the user as long as the token is still valid and a
            user can be found for the email encapsulted in the token """
        try:
            user = cls.query_by_email(token.val(_token))
        except URLTokenExpired:
            raise Registrar.VerificationExpired()
        
        if user is None:
            raise Registrar.BadVerification()
        elif not user.verified:
            user.verified = True
            db.session.commit()
        return user

    @staticmethod
    def unregister(id):
        """ Unregisters a user from the system """
        Balances.query.filter_by(user_id=id).delete()
        Transacted.query.filter_by(user_id=id).delete()
        ClosedPositions.query.filter_by(user_id=id).delete()
        Holdings.query.filter_by(user_id=id).delete()
        UserLocations.query.filter_by(user_id=id).delete()
        TwoFactorAuth.query.filter_by(user_id=id).delete()
        Users.query.filter_by(id=id).delete()
        db.session.commit()

    @staticmethod
    def all():
        """ All of the users registered in the system """
        return Users.query.all()

    @staticmethod
    def query_by_username(username):
        """ The user for the specified username if one exists """
        return Users.query.filter_by(username=username.lower()).first()

    @staticmethod
    def query_by_email(email):
        """ The user for the specified email address if one exists """
        return Users.query.filter_by(email=email).first()

class BasicAuth:
    class BadCredentials(Exception):
        """ Indicates the credentials are bad """
        pass

    class AccountLocked(Exception):
        """ Indicates the account has been locked """
        pass

    @classmethod
    def authenticate(cls, username, password):
        user = Registrar.query_by_username(username)
        if user is None:
            raise cls.BadCredentials()
        elif user.locked:
            raise cls.AccountLocked()
        elif not user.verify_password(password):
            if AccountManager.lock(user):
                raise cls.AccountLocked()
            raise cls.BadCredentials()

        LocationManager.check_location(user)
        return user

class LocationManager:
    """ Access location manager """

    @staticmethod
    def check_location(user):
        """ Checks the location of the client against the location of the user when the account
            was initially logged into to see if the location has changed """
        details = geo.location()
        if details is None:
            return
        
        user_loc = UserLocations.query.filter_by(user_id=user.id).first() 
        if user_loc is None:
            loc = UserLocations(user.id, details)
            db.session.add(loc)
            db.session.commit()
        elif user_loc.loc != details["loc"]:
            mail.send(UnrecognizedAccessMail(user.email, details, token.generate(user.username)))

class TwoFactAuth:
    """ Two Factor Authentication """

    class BadMethod(Exception):
        """ Indicates a bad / unsupported method was specified """
        pass

    class BadOTP(Exception):
        """ Indicates a bad OTP was provided """
        pass

    @classmethod
    def __check_method(cls, method):
        """ Ensures a supported method was specified """
        if not method in ["sms", "mail"]:
            raise cls.BadMethod()

    @classmethod
    def verify(cls, method, dest, code):
        """ Verifies the method, destination and otp are valid"""
        cls.__check_method(method)
        token.val(dest)
        user = UserContext.user()
        if not otp.verify(user, code, session["login_dt_tm"]):
            raise cls.BadOTP()

    @classmethod
    def request_verification(cls, user, method, to):
        """ Verifies the method and sends the OTP code. The destination is tokenized 
            to avoid exposing in the url """
        cls.__check_method(method)
        code = otp.generate(user, session["login_dt_tm"])
        if method == "sms":
            sms.send(OTPSMS(to, code))
        else:
            mail.send(OTPMail(to, code))
        return token.generate(to)

    @classmethod
    def request_again(cls, method, dest):
        """ Verifies the method, destination and resends the OTP code """
        cls.__check_method(method)
        code = otp.generate(UserContext.user(), session["login_dt_tm"])
        to = token.val(dest)
        if method == "sms":
            sms.send(OTPSMS(to, code))
        else:
            mail.send(OTPMail(to, code))

class PortfolioManager:
    """ User Portfolio Manager """

    suggestions = [
        'AAL',
        'AAPL',
        'ACB',
        'AMC',
        'AMD',
        'AMZN',
        'APHA',
        'BA',
        'BABA',
        'BAC',
        'BP',
        'BRK.B',
        'BYND',
        'CCL',
        'CGC',
        'CPRX',
        'CRBP',
        'CRON',
        'DAL',
        'DIS',
        'DKNG',
        'ET',
        'F',
        'FB',
        'FCEL',
        'FIT',
        'GE',
        'GILD',
        'GM',
        'GNUS',
        'GOOGL',
        'GPRO',
        'GPS',
        'GUSH',
        'HAL',
        'HEXO',
        'IBIO',
        'INO',
        'INTC',
        'IVR',
        'JBLU',
        'JNJ',
        'JPM',
        'KO',
        'KODK',
        'KOS',
        'LUV',
        'LYFT',
        'MFA',
        'MGM',
        'MRNA',
        'MRO',
        'MSFT',
        'NCLH',
        'NFLX',
        'NIO',
        'NKE',
        'NKLA',
        'NOK',
        'NRZ',
        'NVAX',
        'NVDA',
        'NYMT',
        'PENN',
        'PFE',
        'PLAY',
        'PLUG',
        'PSEC',
        'PTON',
        'PYPL',
        'RCL',
        'SAVE',
        'SBUX',
        'SIRI',
        'SNAP',
        'SNE',
        'SPCE',
        'SPHD',
        'SPY',
        'SQ',
        'SRNE',
        'T',
        'TLRY',
        'TSLA',
        'TWTR',
        'TXMD',
        'UAL',
        'UBER',
        'UCO',
        'USO',
        'V',
        'VOO',
        'VSLR',
        'WFC',
        'WKHS',
        'WMT',
        'WORK',
        'XOM',
        'ZM',
        'ZNGA']

    @classmethod
    def portfolio(cls):
        """ The user's portfolio """
        positions = []
        t_cost = 0.0
        t_value = 0.0
        t_change = 0.0

        append = positions.append
        lookup = stock.lookup
        for holding in cls.query_holdings_by_user():
            ticker = lookup(holding.symbol)

            cost = Stocks.valuation(holding.price, holding.shares)
            t_cost += cost
            value = Stocks.valuation(ticker["price"], holding.shares)
            t_value += value
            change = value - cost
            t_change += change

            append({
                "name": ticker["name"],
                "symbol": holding.symbol,
                "shares": holding.shares,
                "price": holding.price,
                "latestPrice": ticker["price"],
                "dayChange": ticker["change"],
                "cost": cost,
                "value" : value,
                "change": change
            })

        cash = cls.cash_on_hand()
        t_cost += cash
        t_value += cash    
        append({
                "name": "CASH",
                "symbol": "",
                "shares": 0,
                "price": 1.0,
                "latestPrice": 1.0,
                "dayChange": 0.0,
                "cost": cash,
                "value" : cash,
                "change": 0.0
            })

        return {
            "positions" : positions,
            "cost" : t_cost, 
            "value" : t_value, 
            "change" : t_change,
            "closed_positions" : not ClosedPositions.query.filter_by(user_id=UserContext.id()).first() is None  
        }

    @classmethod
    def insights(cls):
        """ The user's portfolio insights """
        labels = []
        values = []

        labels_append = labels.append
        values_append = values.append
        latest_price = stock.latest_price

        for holding in cls.query_holdings_by_user():
            values_append(Stocks.valuation(latest_price(holding.symbol), holding.shares))
            labels_append(holding.symbol) 

        values_append(cls.cash_on_hand())
        labels_append("CASH")

        return {
            "values" : values,
            "labels" : labels,
            "active" : stock.most_active(), 
            "gainers" : stock.biggest_gainers(), 
            "losers" :stock.biggest_losers()
        }

    @staticmethod
    def closed_positions():
        """ The closed positions for the user """
        t_cost = 0.0
        t_value = 0.0
        t_change = 0.0

        positions = {}
        for position in ClosedPositions.query.filter_by(user_id=UserContext.id()).order_by(ClosedPositions.symbol):
            if not position.symbol in positions:
                positions[position.symbol] = []
            
            cost = Stocks.valuation(position.pps, position.shares)
            t_cost += cost		
            value = Stocks.valuation(position.price, position.shares)
            t_value += value
            change = value - cost
            t_change += change

            positions[position.symbol].append({
                "symbol": position.symbol,
                "shares": position.shares,
                "pps": position.pps,
                "price": position.price,
                "date": position.close_dt_tm,
                "cost": cost,
                "value" : value,
                "change": change
            })
        
        return {
            "positions" : positions,
            "cost" : t_cost, 
            "value" : t_value, 
            "change" : t_change
        }

    @staticmethod
    def position(symbol):
        """ The user's position """
        symbol = symbol.upper()
        holding = Holdings.query.filter_by(user_id=UserContext.id(), symbol=symbol).one()
        ticker = stock.lookup(holding.symbol)
        cost = Stocks.valuation(holding.price, holding.shares)
        value = Stocks.valuation(ticker["price"], holding.shares)

        return {
            "name": ticker["name"],
            "symbol": holding.symbol,
            "shares": holding.shares,
            "pps": holding.price,
            "ppsChange": ticker["price"] - holding.price,
            "price": ticker["price"],
            "dayChange": ticker["change"],
            "cost": cost,
            "value" : value,
            "change": value - cost
        }

    @staticmethod
    def history(page):
        """ The user's transaction history """
        return Transacted.query.filter_by(user_id=UserContext.id()).order_by(Transacted.trans_dt_tm.desc()).paginate(page, 12, False)

    @staticmethod
    def quote(symbol):
        """ The quote for the specified stock """        
        symbol = symbol.upper()
        ticker = stock.lookup(symbol)
        if ticker is None:
            return None
        return {
            "ticker": ticker, 
            "headlines": stock.news(symbol), 
            "share_holder" : not Holdings.query.filter_by(symbol=symbol, user_id=UserContext.id()).first() is None
        }

    @staticmethod
    def cash_on_hand():
        """ The user's cash on hand """
        return UserContext.user().cash

    @staticmethod
    def asking_price(symbol):
        """ The asking price for the stock """
        return stock.latest_price(symbol.upper())

    @staticmethod
    def query_holdings_by_user(user_id=None):
        return Holdings.query.filter_by(user_id=user_id or UserContext.id()).order_by(Holdings.symbol)

    @classmethod
    def holdings(cls):
        """ The user's holdings """
        holdings = []
        append = holdings.append
        for holding in cls.query_holdings_by_user():
            append(holding.asdict())
        return holdings

    @classmethod
    def holding(cls, holding_id):
        """ Returns the holding """
        holding = Holdings.query.filter_by(id=holding_id).first()
        if holding is None:
            return None

        response = holding.asdict()
        response["pps"] = response["price"]
        response["price"] = cls.asking_price(holding.symbol)
        return response

    @classmethod
    def holding_symbols(cls):
        symbols = []

        append = symbols.append
        for holding in cls.query_holdings_by_user():
            append(holding.symbol)

        return symbols

    @classmethod
    def suggested_stocks(cls):
        """ The suggested stocks """
        return cls.suggestions

    @staticmethod
    def buy(symbol, shares):
        """ Purchases stock for the user """
        symbol = symbol.upper()
        ticker = stock.lookup(symbol)
        price = ticker["price"]			
        cost = Stocks.valuation(price, shares)

        user = UserContext.user()
        if user.cash < cost:
            return False        
        user.cash -= cost

        holding = Holdings.query.filter_by(user_id=user.id, symbol=symbol).first()
        if holding is None:
            holding = Holdings(user_id=user.id, symbol=symbol, shares=shares, price=price)			
            db.session.add(holding)
        else:
            holding_shares = holding.shares + shares
            holding_price = round((Stocks.valuation(holding.shares, holding.price) + cost) / holding_shares, 2)
            holding.shares = holding_shares
            holding.price = holding_price
            
        transacted = Transacted(user_id=user.id, type="BUY", name=ticker["name"], symbol=symbol,
                                shares=shares, price=price, cost=cost, trans_dt_tm=Dates.now_utc_str())
        db.session.add(transacted)
        db.session.commit()
        return True

    @staticmethod
    def sell(holding, shares):
        """ Sells the stock for the user """
        holding_shares = holding.shares - shares
        if holding_shares > 0:
            holding.shares = holding_shares
        else :
            db.session.delete(holding)

        ticker = stock.lookup(holding.symbol)
        price = ticker["price"]
        cost = Stocks.valuation(price, shares)

        close_dt_tm = Dates.now_utc_str()
        transacted = Transacted(user_id=holding.user_id, type="SELL", name=ticker["name"], symbol=holding.symbol,
                                shares=shares, price=price, cost=cost, trans_dt_tm=close_dt_tm)
        db.session.add(transacted)

        closed_position = ClosedPositions(user_id=holding.user_id, symbol=holding.symbol, shares=shares, 
            pps=holding.price, price=price, close_dt_tm=close_dt_tm)
        db.session.add(closed_position)

        user = UserContext.user()
        user.cash += cost
        db.session.commit()

    @staticmethod
    def is_market_closed():
        """ Whether the market is open """
        return not Stocks.is_exchange_open()

class AccountManager:
    """ User Account Manager """
    
    class ResetPasswordExpired(Exception):
        """ Indicates the reset password link has expired """
        pass

    class ReusedEmail(Exception):
        """ Indicates an attempt to use the same email """
        pass

    class EmailExists(Exception):
        """ Indicates an attempt to use an email that already exists in the system """
        pass

    @staticmethod
    def lock(user, max_allow=4):
        if not user.locked:
            attempts = session.get("log_in_attempts") 
            if attempts is None:
                attempts = 0
        
            session["log_in_attempts"] = attempts + 1
            if session["log_in_attempts"] >= max_allow:
                user.locked = True
                db.session.commit()
        return user.locked

    @staticmethod
    def __unlock(user):
        attempts = session.get("log_in_attempts") 
        if not attempts is None:
            session["log_in_attempts"] = None
        user.locked = False

    @staticmethod
    def two_fa_enabled():
        """ Whether two factor authentication is enabled """
        return TwoFactorAuth.query.filter_by(user_id=UserContext.id()).one().enabled

    @staticmethod
    def two_fa(enabled):
        """ Toggles whether two factor authentication is enabled """
        auth = TwoFactorAuth.query.filter_by(user_id=UserContext.id()).one()
        if auth.enabled != enabled:
            auth.enabled = enabled
            db.session.commit()
            return True
        return False

    @staticmethod
    def forgot_username(email):
        """ Sends a reminder to the user of what their username is granted they 
            are in the system """
        user = Registrar.query_by_email(email)
        if not user is None:
            mail.send(UsernameMail(user.email, user.username))
            return True
        return False

    @staticmethod
    def forgot_password(username):
        """ Sends a password reset link granted they are in the system """
        user = Registrar.query_by_username(username)
        if not user is None:
            mail.send(PasswordResetMail(user.email, token.generate(user.username)))
            return True
        return False

    @staticmethod
    def change_email(email):
        """ Changes the email associated with the user account assuming:
            1) The email is unique and 2) The email isn't the same """
        user = UserContext.user()
        if user.email == email:
            raise AccountManager.ReusedEmail()
        elif not Registrar.query_by_email(email) is None:
            raise AccountManager.EmailExists()
        user.email = email
        db.session.commit()		

    @classmethod
    def change_password(cls, password, _token=None):
        """ Changes the password associated with the user account """
        try:
            user = UserContext.user() if _token is None else\
                Registrar.query_by_username(token.val(_token))
            if not user.verify_password(password):
                user.password = password
                cls.__unlock(user)
                db.session.commit()
                return True
            return False
        except URLTokenExpired:
            raise AccountManager.ResetPasswordExpired()

    @staticmethod
    def deposit(amount):
        """ Deposits the specified amount in the session user's account """
        user = UserContext.user()
        user.cash += amount

        transacted = Transacted(user_id=user.id, type="DEP", name="CASH", symbol="CASH",
            shares=amount, price=1, cost=amount, trans_dt_tm=Dates.now_utc_str())
        db.session.add(transacted)
        db.session.commit()

    @classmethod
    def update_balances(cls):
        """ Updates the user account balances at the end of the day """
        for user in Registrar.all():
            balance = Balances(user_id=user.id, value=cls.account_balance(user), 
                bal_dt_tm=Dates.now_utc_str())
            db.session.add(balance)
        db.session.commit()
    
    @staticmethod
    def account_balance(user):
        """ Updates the user's account balance accounting for any stock splits that 
            might have occured """
        value = user.cash

        latest_price = stock.latest_price
        for holding in PortfolioManager.query_holdings_by_user(user.id):
            price = latest_price(holding.symbol)
            
            split = Stocks.is_split(holding.price, price, holding.shares)
            if not split is None:
                holding.shares = split["shares"]
                holding.price = split["pps"]
            value += Stocks.valuation(price, holding.shares)        
        
        return value
