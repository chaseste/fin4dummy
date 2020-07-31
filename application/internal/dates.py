"""Application date utilities."""
from datetime import datetime, time
from dateutil import tz

class Dates:
    @staticmethod
    def now_utc_str() -> str:
        """The current time in UTC as a string in ISO format"""
        utc_zone = tz.gettz('UTC')
        utc = datetime.utcnow()
        utc = utc.replace(tzinfo=utc_zone)
        return utc.strftime("%Y-%m-%dT%H:%M:%S.%f%z")

    @staticmethod
    def now_eastern() -> datetime:
        """Current Us/Eastern date time"""
        return datetime.now(tz.gettz("US/Eastern"))

    @staticmethod
    def is_time_between(begin_time: time, end_time: time, check_time: time = None) -> bool:
        """Checks if the time is between the specified date range"""    
        check_time = check_time or datetime.now().time()
        if begin_time < end_time:
            return check_time >= begin_time and check_time <= end_time
        else:
            return check_time >= begin_time or check_time <= end_time

    @staticmethod
    def is_week_day(check_date: datetime = None) -> bool:
        """Determines if its the weekday"""
        check_date = check_date or datetime.now()
        return not check_date.weekday() in [5, 6]
