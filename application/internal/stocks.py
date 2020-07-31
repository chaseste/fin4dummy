"""Stock APIs."""
from typing import Dict, List, Optional, Union

from cachetools import cached, TTLCache
from googletrans import Translator
from datetime import time

from .utils import to_float, call_api, quote
from .dates import Dates

class Stocks:
    """ Stock API."""

    @staticmethod
    def is_exchange_open() -> bool:
        """Determines if the exchange is open (doesn't account for holidays)"""
        check_date = Dates.now_eastern()
        return Dates.is_week_day(check_date) and Dates.is_time_between(time(9,30), time(16, 30), check_date.time())

    @staticmethod
    def valuation(price:float, shares:int) -> float:
        """Calculate the value of the stock."""
        return round(price * shares, 2)

    @staticmethod
    def is_split(pps:float, price:float, shares:int) -> dict:        
        split = True if pps >= 100.0 and round(price / pps, 2) <= 0.5 else False
        if not split:
            return None
        
        ratio = int(round(pps / price))
        return {
            "pps": round(pps / ratio, 2),
            "shares": shares * ratio
        }

    def __init__(self, app=None):
        if app is not None:
            self.init(app)

    def init(self, app) -> None:
        self.iex_api_key = app.config["IEX_API_KEY"]

    def __defaults(self, data: Dict[str, Union[str, float]]) -> Dict[str, Union[str, float]]:
        # This is not ideal though the IEX doesn't update these during the day so we'll 
        # default them until the data is available after the market has closed....
        if "low" in data and data["low"] == 0.0:
            data["low"] = data["price"] 
        if "high" in data and data["high"] == 0.0:
            data["high"] = data["price"]
        if "open" in data and data["open"] == 0.0:
            data["open"] = data["price"]
        return data

    def __map_news(self, headlines: List[Dict[str, str]]) -> List[Dict[str, str]]:
        translator = Translator()
        translate = translator.translate
        for headline in headlines:
            headline["src_lang"] = headline["lang"]
            if headline["lang"] != "en":
                headline["headline"] = translate(headline["headline"]).text
                headline["summary"] = translate(headline["summary"]).text
                headline["lang"] = "en"
        return headlines
        
    def __map_market_data(self, market_data: List[Dict[str, str]]) -> List[Dict[str, Union[str, float]]]:
        stocks = []
        append = stocks.append
        defaults = self.__defaults 
        for data in market_data:
            append(defaults({
                "symbol": data["symbol"],
                "name": data["companyName"],
                "price": to_float(data["latestPrice"]),
                "high" : to_float(data["high"]),
                "low" : to_float(data["low"]),
                "change" : to_float(data["change"]),
                "changePercent": round(to_float(data["changePercent"]) * 100, 2)}))
        return stocks

    def __latest_price_url(self, symbol: str) -> str:
        return f"https://cloud-sse.iexapis.com/stable/stock/{quote(symbol)}/quote/latestPrice?token={self.iex_api_key}"

    def __quote_url(self, symbol: str) -> str:
        return f"https://cloud-sse.iexapis.com/stable/stock/{quote(symbol)}/quote?token={self.iex_api_key}"

    def __news_url(self, symbol: str) -> str:
        return f"https://cloud-sse.iexapis.com/stable/stock/{quote(symbol)}/news/last/3?token={self.iex_api_key}"

    def __most_active_url(self) -> str:
        return f"https://cloud-sse.iexapis.com/stable/stock/market/list/mostactive?token={self.iex_api_key}"

    def __gainers_url(self) -> str:
        return f"https://cloud-sse.iexapis.com/stable/stock/market/list/gainers?token={self.iex_api_key}"

    def __losers_url(self) -> str:
        return f"https://cloud-sse.iexapis.com/stable/stock/market/list/losers?token={self.iex_api_key}"

    @cached(cache=TTLCache(maxsize=100, ttl=900))
    def latest_price(self, symbol: str) -> Optional[float]:
        """Look up the latest price for symbol."""
        return call_api(self.__latest_price_url(symbol), lambda data: to_float(data))

    @cached(cache=TTLCache(maxsize=100, ttl=900))
    def lookup(self, symbol: str) -> Optional[Dict[str, Union[str, float]]]:
        """Look up quote for symbol."""
        return call_api(self.__quote_url(symbol), lambda data : self.__defaults({
                "symbol": data["symbol"],
                "name": data["companyName"],
                "price": to_float(data["latestPrice"]),
                "open" : to_float(data["open"]),
                "high" : to_float(data["high"]),
                "low" : to_float(data["low"]),
                "previousClose" : to_float(data["previousClose"]), 
                "change" : to_float(data["change"]),
                "changePercent": round(to_float(data["changePercent"]) * 100, 2),
                "peRatio": to_float(data["peRatio"]),
                "52WeekHigh" : to_float(data["week52High"]),
                "52WeekLow" : to_float(data["week52Low"]),
                "ytdChange": round(to_float(data["ytdChange"]) * 100, 2)
            }))

    @cached(cache=TTLCache(maxsize=100, ttl=900))
    def news(self, symbol: str) -> Optional[List[Dict[str, str]]]:
        """Look up news for symbol."""
        return call_api(self.__news_url(symbol), self.__map_news)

    @cached(cache=TTLCache(maxsize=1, ttl=900))
    def most_active(self: str) -> List[Dict[str, Union[str, float]]]:
        """Look up the most active stocks."""
        return call_api(self.__most_active_url(), self.__map_market_data, [])

    @cached(cache=TTLCache(maxsize=1, ttl=900))
    def biggest_gainers(self: str) -> List[Dict[str, Union[str, float]]]:
        """Look up the biggest gainer stocks."""
        return call_api(self.__gainers_url(), self.__map_market_data, [])

    @cached(cache=TTLCache(maxsize=1, ttl=900))
    def biggest_losers(self: str) -> List[Dict[str, Union[str, float]]]:
        """Look the biggest loser stocks."""
        return call_api(self.__losers_url(), self.__map_market_data, [])
