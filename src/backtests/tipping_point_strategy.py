import datetime

from data_parser import price_data_parser
from utils.config import BASE_PATH
from position import Position
from evaluation import sharpe_ratio

"""
分析：
    对比上涨下跌，过去 30 天的高点并不能作为一个清晰的买入卖出点，很多都是在一个迅速上升的半山腰，但是买入点的迹象比较明显，
    过去 30 天的低点买入就是一个比较好的方案，甚至可以是过去 15 天的低点
策略： todo
    买入: 
        1. 在一段时间价格最低时进行买入，买入一定比例；
        2. 如果价格进一步下跌，每下跌 10% 加仓一定比例；
    卖出:
        1. 如果价格上涨，基于当前成本进行计算，每盈利 5% 卖出一定比例的持仓
        2. 简单考虑 => 由于买入价格够低，持仓直到满足盈利条件 
"""


class TippingPointStrategy(object):

    # FILE_PATH = BASE_PATH + "/data/eth_usd_20230628.csv"
    FILE_PATH = BASE_PATH + "/data/eth_usd_polygon_20230703.csv"

    def __init__(self, init_usd, trade_amount, fee_rate, is_train=False, is_test=False):
        self.trade_amount = trade_amount
        self.fee_rate = fee_rate
        self._init_data(is_train, is_test)
        self.position = Position(0, init_usd, self.fee_rate)
        self.trade_history = []  # (daytime, price, amount, "S"/"B")
        self.cost = 0

    def _init_data(self, is_train, is_test):
        train_start = "0000-00-00"
        train_end = "2023-03-21"
        if is_train:
            self.data = price_data_parser.parse_polygon_data(self.FILE_PATH, train_start, train_end)
        elif is_test:
            self.data = price_data_parser.parse_polygon_data(self.FILE_PATH, train_end)
        else:
            self.data = price_data_parser.parse_polygon_data(self.FILE_PATH, train_start)

    def _on_sell(self, daytime, sell_price, amount):
        try:
            self.position.sell(sell_price, amount)
            self.trade_history.append((daytime, sell_price, amount, "S"))
        except Exception as e:
            print(daytime, e)
            return False

    def _on_buy(self, daytime, buy_price, amount):
        try:
            self.position.buy(buy_price, amount)
            self.trade_history.append((daytime, buy_price, amount, "B"))
        except Exception as e:
            print(daytime, e)
            return False

    def _is_period_lowest(self, daytime, price, period):
        is_lowest = True
        start_datetime = (datetime.datetime.strptime(daytime, "%Y-%m-%d") - datetime.timedelta(days=period)).strftime(
            "%Y-%m-%d")
        for d in self.data:
            current_daytime = d["datetime"]
            current_price = d["price"]
            if current_daytime < start_datetime:
                continue
            if current_daytime > daytime:
                break
            if current_price < price:
                is_lowest = False
                break
        return is_lowest

    def on_trade(self, period):
        for d in self.data[period:]:
            daytime = d["datetime"]
            price = d["price"]
            is_lowest = self._is_period_lowest(daytime, price, period)
            if is_lowest:

