import datetime

from data_parser import price_data_parser
from utils.config import BASE_PATH
from entity.position import Position
from entity.uniswap_trade import Trade, TradeType

"""
分析：
    对比上涨下跌，过去 30 天的高点并不能作为一个清晰的买入卖出点，很多都是在一个迅速上升的半山腰，但是买入点的迹象比较明显，
    过去 30 天的低点买入就是一个比较好的方案，甚至可以是过去 15 天的低点
策略： 
    买入: 
        1. 在一段时间价格最低时进行买入，买入一定比例；
        2. 如果价格进一步下跌，每下跌 10% 加仓一定比例；
        3. 买入价格低是确定性赚钱 => 设定买入价格上限
    卖出:
        1. 如果价格上涨，基于当前成本进行计算，每盈利 10% 卖出一定比例的持仓
        2. 简单考虑 => 由于买入价格够低，持仓直到满足盈利条件
"""


class TippingPointStrategy(object):

    def __init__(self, init_usd, trade_amount, fee_rate, file_path, is_polygon_data, buy_limit=None):
        self.trade_amount = trade_amount
        self.fee_rate = fee_rate
        self.is_polygon = is_polygon_data
        self.buy_limit = buy_limit

        self._init_data(file_path)
        self.position = Position(0, init_usd, self.fee_rate)
        self.trade_history = []  # (daytime, price, amount, "S"/"B")
        self.max_drawdown_list = []
        self.cost = 0
        self.buy_cnt = 0
        self.sell_cnt = 0
        self.last_buy_price = 0

    def _init_data(self, file_path):
        if self.is_polygon:
            self.data = price_data_parser.parse_polygon_data(file_path, "2022-06-01 00:00:00")
        else:
            self.data = price_data_parser.parse_yahoo_data(file_path, "2022-06-01")

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
            trade = Trade(TradeType.SELL, daytime, sell_price, self.position.current_eth)
            self.trade_history.append(trade)
            self.sell_cnt += 1

            self.cost = 0
            self.last_buy_price = 0
            self.print_trade_result(daytime, sell_price, "S")
            max_drawdown_data = self.max_drawdown_list[-1]
            # print("max drawdown:", max_drawdown_data[0], "max drawdown rate:", max_drawdown_data[1],
            #       "max drawdown price:", max_drawdown_data[2])
        except Exception as e:
            print(daytime, e)
            return False

    def _on_buy(self, daytime, buy_price, amount):
        try:
            self.position.buy(buy_price, amount)
            trade = Trade(TradeType.BUY, daytime, buy_price, self.position.current_eth)
            self.trade_history.append(trade)
            self.buy_cnt += 1

            self.cost = (self.cost * (self.position.current_eth - amount) + amount * buy_price
                         ) / self.position.current_eth
            self.last_buy_price = buy_price
            self.print_trade_result(daytime, buy_price, "B")
        except Exception as e:
            print(daytime, e)
            return False

    def _get_period_start(self, end_datetime, period):
        # polygon data
        if self.is_polygon:
            start_datetime = (datetime.datetime.strptime(end_datetime, "%Y-%m-%d %H:%M:%S") - datetime.timedelta(
                days=period)).strftime("%Y-%m-%d %H:%M:%S")
        else:
            start_datetime = (datetime.datetime.strptime(end_datetime, "%Y-%m-%d") - datetime.timedelta(
                days=period)).strftime("%Y-%m-%d")
        return start_datetime

    def _is_period_lowest(self, daytime, price, period):
        is_lowest = True
        start_datetime = self._get_period_start(daytime, period)

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
        start_datetime = self._get_period_start(daytime, period)

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

    def main(self, period):
        position_day_cnt = 0
        buy_cnt = 0
        sell_cnt = 0

        max_drawdown_tuple = (0, 0, 0) # drawdown, price, drawdown_rate

        start = period
        if self.is_polygon:
            start = period * 24

        for d in self.data[start:]:
            daytime = d["datetime"]
            price = d["price"]

            # 同时计算与这段时间高点价格的对比
            highest_price = self._get_period_highest_price(daytime, period)
            diff_rate = (price - highest_price) / highest_price

            # 当已经有持仓的时候
            if self.position.current_eth > 0:
                position_day_cnt += 1
                # 计算基于当前价格的回撤并判断最大回撤
                drawdown = self.calculate_drawdown(price)
                if drawdown < max_drawdown_tuple[0]:
                    max_drawdown_tuple = (drawdown, price, drawdown / (self.cost * self.position.current_eth))

                # 如果当前价格高于成本价 10% 进行卖出
                if price > self.cost * 1.1:
                    self.max_drawdown_list.append(max_drawdown_tuple)
                    self._on_sell(daytime, price, self.trade_amount)
                    sell_cnt += 1

                    max_drawdown_tuple = (0, 0, 0)
                    continue

                # 持仓情况下，之前已经买过，计算新价格是否满足继续买入的条件
                decrease_rate = (price - self.last_buy_price) / self.last_buy_price
                if decrease_rate < -0.1:
                    self._on_buy(daytime, price, self.trade_amount)
                    buy_cnt += 1
                    print("highest_price:", highest_price, "price:", price, "diff rate:", diff_rate)
                continue

            # 未持仓情况下，计算是否是 period 期间最低价
            is_lowest = self._is_period_lowest(daytime, price, period)
            if not is_lowest:
                continue

            # 如果与高点价格比较低于 10% 的变化或者价格高于购买价格上限，不进行买入
            if diff_rate > -0.1 or (self.buy_limit is not None and price >= self.buy_limit):
                print("Not buying, highest_price:", highest_price, "price:", price, "diff rate:", diff_rate, "day:",
                      daytime)
                continue

            self._on_buy(daytime, price, self.trade_amount)
            buy_cnt += 1
            print("highest_price:", highest_price, "price:", price, "diff rate:", diff_rate)

        position_rate = position_day_cnt / (len(self.data) - start)
        # ploygon data
        if self.is_polygon:
            position_day_cnt /= 24
        print("buy cnt:", buy_cnt, "sell cnt:", sell_cnt, "pos day:", position_day_cnt, "pos day rate:",
              position_rate, "average pos day:", position_day_cnt / sell_cnt)
        return self.trade_history


if __name__ == '__main__':
    # filepath = BASE_PATH + "/data/eth_usd_20230710.csv"
    filepath = BASE_PATH + "/data/eth_usd_polygon_20230714.csv"

    init_usd = 3000
    trade_amount = 1
    trading_fee = 0.0006
    buy_limit = 1800
    tipping_point_strategy = TippingPointStrategy(init_usd, trade_amount, trading_fee, filepath, False, buy_limit)

    period = 15
    trade_history = tipping_point_strategy.main(period)
    # print("trade history:", trade_history)
