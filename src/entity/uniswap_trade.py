from enum import Enum

from utils import math_utils


class TradeType(Enum):
    BUY = 1
    SELL = 2
    CONTINUE_BUY = 3
    CONTINUE_SELL = 4
    REVERSE_BUY = 5
    REVERSE_SELL = 6


class UniswapTrade(object):
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


class Trade(object):

    def __init__(self, type, time, price, amount):
        self._type = type
        self._time = time
        self._price = price
        self._amount = amount

    @property
    def type(self):
        return self._type

    @property
    def time(self):
        return self._time

    @property
    def price(self):
        return self._price

    @property
    def amount(self):
        return self._amount

    def __str__(self):
        return "trade_type: {}, datetime: {}, price: {}, amount: {}".format(self._type.name, self._time, self._price,
                                                                            self._amount)
