from enum import Enum

from utils import math_utils


class TradeType(Enum):
    BUY = 1
    SELL = 2
    CONTINUE_BUY = 3
    CONTINUE_SELL = 4
    REVERSE_BUY = 5
    REVERSE_SELL = 6
    BUY_LIST = [BUY, CONTINUE_BUY, REVERSE_BUY]
    SELL_LIST = [SELL, CONTINUE_SELL, REVERSE_SELL]


class Trade(object):
    def __init__(self, trade_type, timestamp, price, amount):
        self._trade_type = trade_type
        self._timestamp = timestamp
        self._price = price
        self._tick = math_utils.price_to_tick(price)
        self._amount = amount

    @property
    def trade_type(self):
        return self._trade_type

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def price(self):
        return self._price

    @property
    def tick(self):
        return self._tick

    @property
    def amount(self):
        return self._amount
