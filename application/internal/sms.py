from twilio.rest import Client 

class SMS:
    def __init__(self, to: str, message: str):
        self.to = to
        self.message = message

class OTPSMS(SMS):
    """OTP SMS."""
    def __init__(self, to: str, token: str):
        super().__init__(to, f"Your F$n4dummy OTP is {token}")

class SMSs:
    """ SMS Service."""
    def __init__(self, app=None):
        if app is not None:
            self.init(app)

    def init(self, app) -> None:
        self.sid = app.config["TWILIO_SID"]
        self.token = app.config["TWILIO_TOKEN"]
        self.number = app.config["TWILIO_NUMBER"]

    def __send_sms(self, to: str, message: str) -> None:
        client = Client(self.sid, self.token)
        client.messages.create(from_=self.number, body=message, to=to)

    def send(self, sms: SMS) -> None:
        self.__send_sms(sms.to, sms.message)
