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

    FILE_PATH = BASE_PATH + "/data/eth_usd_20230710.csv"
    # FILE_PATH = BASE_PATH + "/data/eth_usd_polygon_20230712.csv"

    def __init__(self, init_usd, trade_amount, fee_rate, is_train=False, is_test=False):
        self.trade_amount = trade_amount
        self.fee_rate = fee_rate
        self._init_data(is_train, is_test)
        self.position = Position(0, init_usd, self.fee_rate)
        self.trade_history = []  # (daytime, price, amount, "S"/"B")
        self.max_drawdown_list = []
        self.cost = 0
        self.last_buy_value = 0
        self.last_buy_price = 0

    def _init_data(self, is_train, is_test):
        train_start = "2022-06-01"
        train_end = "2023-03-21"
        # if is_train:
        #     self.data = price_data_parser.parse_polygon_data(self.FILE_PATH, train_start, train_end)
        # elif is_test:
        #     self.data = price_data_parser.parse_polygon_data(self.FILE_PATH, train_end)
        # else:
        #     self.data = price_data_parser.parse_polygon_data(self.FILE_PATH, train_start)
        if is_train:
            self.data = price_data_parser.parse_yahoo_data(self.FILE_PATH, train_start, train_end)
        elif is_test:
            self.data = price_data_parser.parse_yahoo_data(self.FILE_PATH, train_end)
        else:
            self.data = price_data_parser.parse_yahoo_data(self.FILE_PATH, train_start)

    def _on_sell(self, daytime, sell_price, amount):
        try:
            # 分部卖出
            # self.position.sell(sell_price, amount)
            # self.trade_history.append((daytime, sell_price, amount, "S"))
            # if self.position.current_eth == 0:
            #     self.cost = 0
            # 只考虑买入成本，如果考虑卖出降成本，则会降低收益率
            # else:
            #     self.cost = (self.cost * (self.position.current_eth + amount) - amount * sell_price) / self.position.current_eth

            # 一次性卖出
            self.position.sell(sell_price, self.position.current_eth)
            self.trade_history.append((daytime, sell_price, self.position.current_eth, "S"))
            self.cost = 0
            self.last_buy_price = 0
            # self.last_buy_value = 0

            self.print_trade_result(daytime, sell_price, "S")
            max_drawdown_data = self.max_drawdown_list[-1]
            print("max drawdown:", max_drawdown_data[0], "max drawdown rate:", max_drawdown_data[1],
                  "max drawdown price:", max_drawdown_data[2])
        except Exception as e:
            print(daytime, e)
            return False

    def _on_buy(self, daytime, buy_price, amount):
        try:
            self.position.buy(buy_price, amount)
            self.trade_history.append((daytime, buy_price, amount, "B"))
            self.cost = (self.cost * (self.position.current_eth - amount) + amount * buy_price) / self.position.current_eth
            self.last_buy_price = buy_price
            # self.last_buy_value = self.position.current_eth * self.cost + self.position.current_usd
            self.print_trade_result(daytime, buy_price, "B")
        except Exception as e:
            print(daytime, e)
            return False

    def _is_period_lowest(self, daytime, price, period):
        is_lowest = True
        # yahoo data
        start_datetime = (datetime.datetime.strptime(daytime, "%Y-%m-%d") - datetime.timedelta(days=period)).strftime(
            "%Y-%m-%d")
        # polygon data
        # start_datetime = (datetime.datetime.strptime(daytime, "%Y-%m-%d %H:%M:%S") - datetime.timedelta(days=period)
        #                   ).strftime("%Y-%m-%d %H:%M:%S")
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

    def _get_period_highest_price(self, daytime, period):
        # yahoo data
        start_datetime = (datetime.datetime.strptime(daytime, "%Y-%m-%d") - datetime.timedelta(days=period)).strftime(
            "%Y-%m-%d")
        # polygon data
        # start_datetime = (datetime.datetime.strptime(daytime, "%Y-%m-%d %H:%M:%S") - datetime.timedelta(days=period)
        #                   ).strftime("%Y-%m-%d %H:%M:%S")
        highest_price = 0
        for d in self.data:
            current_daytime = d["datetime"]
            current_price = d["price"]
            if current_daytime < start_datetime:
                continue
            if current_daytime > daytime:
                break
            if highest_price < current_price:
                highest_price = current_price
        return highest_price

    def print_trade_result(self, daytime, price, trade_type):
        print("date: ", daytime, "trade price: ", price, "trade_type:", trade_type, self.position, "cost:", self.cost,
              "profit:", self.position.get_profit(price), "profit rate:", self.position.get_profit_rate(price))

    def calculate_drawdown(self, price):
        return self.position.current_eth * price - self.position.current_eth * self.cost
        # return self.position.current_eth * price + self.position.current_usd - self.last_buy_value

    def main(self, period):
        position_day_cnt = 0
        buy_cnt = 0
        sell_cnt = 0

        # yahoo data
        max_drawdown = 0
        max_drawdown_rate = 0
        max_drawdown_price = 0
        for d in self.data[period:]:
        # polygon data
        # for d in self.data[period * 24:]:
            daytime = d["datetime"]
            price = d["price"]

            if self.position.current_eth > 0:
                position_day_cnt += 1
                drawdown = self.calculate_drawdown(price)
                if drawdown < max_drawdown:
                    max_drawdown = drawdown
                    max_drawdown_price = price
                    max_drawdown_rate = max_drawdown / (self.cost * self.position.current_eth)

                if price > self.cost * 1.1:
                    self.max_drawdown_list.append((max_drawdown, max_drawdown_rate, max_drawdown_price))
                    self._on_sell(daytime, price, self.trade_amount)
                    sell_cnt += 1
                    max_drawdown = 0
                    max_drawdown_rate = 0
                    max_drawdown_price = 0
                    continue

            if self.last_buy_price != 0:
                decrease_rate = (price - self.last_buy_price) / self.last_buy_price
                if decrease_rate < -0.1:
                    self._on_buy(daytime, price, self.trade_amount)
                    buy_cnt += 1
                continue

            is_lowest = self._is_period_lowest(daytime, price, period)
            if not is_lowest:
                continue

            # 增加与这段时间高点价格的对比
            highest_price = self._get_period_highest_price(daytime, period)
            diff_rate = (price - highest_price) / highest_price
            if diff_rate > -0.1:
                continue

            self._on_buy(daytime, price, self.trade_amount)
            buy_cnt += 1
            # print("highest_price:", highest_price, "price:", price, "diff rate:", diff_rate)

        print("buy cnt:", buy_cnt, "sell cnt:", sell_cnt, "pos day:", position_day_cnt, "pos day rate:",
              position_day_cnt / (len(self.data) - period))
        print(self.max_drawdown_list)


if __name__ == '__main__':
    init_usd = 3000
    trade_amount = 1
    trading_fee = 0.0006
    tipping_point_strategy = TippingPointStrategy(init_usd, trade_amount, trading_fee)

    period = 15
    tipping_point_strategy.main(period)
