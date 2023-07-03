import copy

from data_parser import price_data_parser
from utils.config import BASE_PATH
from position import Position


class PressureSupportStrategy(object):

    def __init__(self, trade_price_dict, trade_amount, fee_rate):
        self.trade_price_dict = trade_price_dict
        self.trade_amount = trade_amount
        self.fee_rate = fee_rate
        self.data = price_data_parser.parse_polygon_data(self.FILE_PATH, "2023-03-21")
        self.position = None
        self.trade_history = []

    def on_trade(self, datetime, price):
        sell_price_list = self.trade_price_dict["sell"]
        buy_price_list = self.trade_price_dict["buy"]
        last_trade = self.trade_history[-1] if self.trade_history else None
        # sell
