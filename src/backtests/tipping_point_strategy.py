from data_parser import price_data_parser
from utils.config import BASE_PATH
from position import Position
from evaluation import sharpe_ratio

"""
分析：
    对比上涨下跌，过去 30 天的高点并不能作为一个清晰的买入卖出点，很多都是在一个迅速上升的半山腰，但是买入点的迹象比较明显，
    过去 30 天的低点买入就是一个比较好的方案，甚至可以是过去 15 天的低点
策略：
    买入 —— 15 天低点买入 25%; 同时是 30 天低点的话再买入 25%；价格每次相对上次买入下跌 10%，再买入 25%
"""


class TippingPointStrategy(object):

    # FILE_PATH = BASE_PATH + "/data/eth_usd_20230628.csv"
    FILE_PATH = BASE_PATH + "/data/eth_usd_polygon_20230703.csv"

    def __init__(self, init_usd, trade_amount, fee_rate, is_train=False, is_test=False):
        self.trade_amount = trade_amount
        self.fee_rate = fee_rate
        self._init_data(is_train, is_test)
        self.position = Position(0, init_usd, self.fee_rate)
        self.trade_history = []  # (datetime, price, amount, "S"/"B")

    def _init_data(self, is_train, is_test):
        train_start = "0000-00-00"
        train_end = "2023-03-21"
        if is_train:
            self.data = price_data_parser.parse_polygon_data(self.FILE_PATH, train_start, train_end)
        elif is_test:
            self.data = price_data_parser.parse_polygon_data(self.FILE_PATH, train_end)
        else:
            self.data = price_data_parser.parse_polygon_data(self.FILE_PATH, train_start)
