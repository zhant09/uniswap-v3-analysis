import copy
import pandas as pd

from position import Position


"""
caution: 
    In order to fix the cross board problem, set the board somewhere near but not exact.
    For example, if the board is (1700, 1800) and (1800, 1900)
        when cross the 1800 board downside, the sell happens on 1810
        when cross the 1800 board upside, the buy happens on 1790
        when the price between 1790 and 1810, it could be in either (1710, 1790) or (1810, 1890) range amount, 
            and no trade will happen between the gap 
"""

class PressureSupportStrategy(object):

    def __init__(self, trade_price_list, trade_gap, trade_amount, fee_rate, init_price):
        self.trade_price_list = trade_price_list
        self.trade_amount = trade_amount
        self.fee_rate = fee_rate
        self._init_base(trade_gap, init_price)
        self.trade_history = [] # tuple element: (day, day_price, price_range)

    def _init_base(self, trade_gap, init_price):
        price_range_list = copy.deepcopy(self.trade_price_list)
        price_range_list.insert(0, 0)
        price_range_list.append(100000)

        range_amount_dict = {}
        for i, trade_price in enumerate(price_range_list[:-1]):
            next_trade_price = price_range_list[i+1]
            amount = self.trade_amount * (len(price_range_list) - 2 - i)
            range_amount_dict[(trade_price + trade_gap, next_trade_price - trade_gap)] = amount
            if trade_price < init_price <= next_trade_price:
                # this init way is to make the usd capital usage most efficient
                init_usd = 2000 * self.trade_amount * len(self.trade_price_list) - 2000 * amount
                self.position = Position(amount, init_usd, self.fee_rate)
        self.range_amount_dict = range_amount_dict
        self.amount_range_dict = {v: k for k, v in self.range_amount_dict.items()}

    def _get_predefined_amount(self, price):
        for price_range, amount in self.range_amount_dict.items():
            if price_range[0] <= price <= price_range[1]:
                return amount
        return None

    def _get_trade_price_list(self, price):
        current_range = self.amount_range_dict[self.position.current_eth]


    def on_trade(self, price):
        predefined_amount = self._get_predefined_amount(price)
        if predefined_amount is None or predefined_amount == self.position.current_eth:
            return None
        # buy situation
        if self.position.current_eth - predefined_amount > 0:
            current_range = self.amount_range_dict[self.position.current_eth]


    def main(self):






