import json
import os
from pathlib import Path
import pytz
from datetime import datetime, timedelta, timezone

class AppTime:
    def __init__(self, tz_str="UTC-3"):
        self.set_timezone(tz_str)

    def set_timezone(self, tz_str):
        try:
            if tz_str.startswith("UTC"):
                offset_hours = int(tz_str[3:])
                self.tz = timezone(timedelta(hours=offset_hours))
            else:
                self.tz = pytz.timezone(tz_str)
        except Exception:
            self.tz = timezone(timedelta(hours=-3))  # Default UTC-3

    def now(self):
        return datetime.now(self.tz)

    def to_local(self, dt_utc):
        if dt_utc.tzinfo is None:
            dt_utc = dt_utc.replace(tzinfo=timezone.utc)
        return dt_utc.astimezone(self.tz)

    def from_local(self, dt_local):
        if dt_local.tzinfo is None:
            dt_local = dt_local.replace(tzinfo=self.tz)
        return dt_local.astimezone(timezone.utc)
    def format(self, dt, fmt="%Y-%m-%d %H:%M:%S"):
        return dt.strftime(fmt)
    def parse(self, date_str, fmt="%Y-%m-%d %H:%M:%S"):
        return datetime.strptime(date_str, fmt).replace(tzinfo=self.tz)