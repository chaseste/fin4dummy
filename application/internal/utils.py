import requests
import urllib.parse

from typing import Optional

def escape(s: str) -> str:
    for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                        ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
        s = s.replace(old, new)
    return s

def quote(s: str) -> str:
    return urllib.parse.quote_plus(s)

def to_float(value: Optional[str]) -> str:
    return 0.0 if value is None else float(value)

def call_api(url, mapper=None, default_return_val=None):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(str(e))
        return default_return_val
    
    try:
        return response.json() if mapper is None else mapper(response.json())
    except (KeyError, TypeError, ValueError) as e:
        print(str(e))
        return default_return_val
