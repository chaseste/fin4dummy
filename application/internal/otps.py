import pyotp
import datetime

from base64 import b32encode 

class OTPs:
    """ OTP Service."""
    def __otp(self, user) -> pyotp.HOTP:
        return pyotp.HOTP(b32encode(user.email.encode()))

    def generate(self, user, for_time: datetime) -> str:
        return self.__otp(user).at(int(for_time.timestamp())) 

    def verify(self, user, otp: str, for_time: datetime) -> bool:
        return self.__otp(user).verify(otp, int(for_time.timestamp()))
