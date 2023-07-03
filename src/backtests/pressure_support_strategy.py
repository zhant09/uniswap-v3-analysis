import copy

from data_parser import price_data_parser
from utils.config import BASE_PATH
from position import Position


class PressureSupportStrategy(object):

    # FILE_PATH = BASE_PATH + "/data/eth_usd_20230628.csv"
    FILE_PATH = BASE_PATH + "/data/eth_usd_polygon_20230628.csv"

    def __init__(self, trade_price_dict, init_eth, init_usd, trade_amount, fee_rate):
        self.trade_price_dict = trade_price_dict
        self.trade_amount = trade_amount
        self.fee_rate = fee_rate
        self.data = price_data_parser.parse_polygon_data(self.FILE_PATH, "2023-03-21")
        self.position = Position(init_eth, init_usd)
        self.trade_history = []  # (datetime, price, "S"/"B")

    def on_trade(self, datetime, price):
        sell_price_list = self.trade_price_dict["sell"]
        buy_price_list = self.trade_price_dict["buy"]
        last_trade = self.trade_history[-1] if self.trade_history else None
        # sell
        if last_trade is None:
            if price >= sell_price_list[0]:
                self.position.sell(price, self.trade_amount)
                self.trade_history.append((datetime, price, "S"))