import copy

from data_parser import price_data_parser
from utils.config import BASE_PATH
from entity.position import Position

"""
caution: 
    In order to fix the cross board problem, set the board somewhere near but not exact.
    For example, if the board is (1700, 1800) and (1800, 1900)
        when cross the 1800 board downside, the sell happens on 1810
        when cross the 1800 board upside, the buy happens on 1790
        when the price between 1790 and 1810, it could be in either (1710, 1790) or (1810, 1890) range amount, 
            and no trade will happen between the gap
core:
    the main idea is in every range, there should be a predefined eth amount, if not matched, the trade happens
analysis:
    when price fluctuate in the range, and finally in a low position, the buy price might be too high, 
        the average cost should be considered in trade_price_list => buy low strategy
"""


class PressureSupportDynamicStrategy(object):

    # FILE_PATH = BASE_PATH + "/data/eth_usd_20230628.csv"
    FILE_PATH = BASE_PATH + "/data/eth_usd_polygon_20230703.csv"

    def __init__(self, trade_price_list, trade_gap, trade_amount, fee_rate, init_eth=None, init_usd=None):
        self.trade_price_list = trade_price_list
        self.trade_gap = trade_gap
        self.trade_amount = trade_amount
        self.fee_rate = fee_rate
        self.data = price_data_parser.parse_hourly_data(self.FILE_PATH, "2023-03-21")
        # self.data = price_data_parser.parse_yahoo_data(self.FILE_PATH, "2023-03-21")
        self._init_base(init_eth, init_usd)
        self.trade_history = []

    def _init_base(self, init_eth, init_usd):
        price_range_list = copy.deepcopy(self.trade_price_list)
        price_range_list.insert(0, 0)
        price_range_list.append(100000)

        range_amount_list = []
        auto_init = False
        if init_eth is not None:
            self.position = Position(init_eth, init_usd, self.fee_rate)
        else:
            auto_init = True
        for i, trade_price in enumerate(price_range_list[:-1]):
            next_trade_price = price_range_list[i + 1]
            amount = self.trade_amount * (len(price_range_list) - 2 - i)
            range_amount_list.append((trade_price + self.trade_gap, next_trade_price - self.trade_gap, amount))
            # this init way is to make the usd capital usage most efficient based on the start price
            if auto_init and trade_price < self.data[0]["price"] <= next_trade_price:
                init_usd = 2000 * self.trade_amount * len(self.trade_price_list) - 2000 * amount
                self.position = Position(amount, init_usd, self.fee_rate)
        self.range_amount_list = range_amount_list

        self.amount_range_dict = dict()
        for start_price, end_price, amount in self.range_amount_list:
            self.amount_range_dict[amount] = (start_price, end_price)

    def _get_predefined_amount(self, price):
        for start_price, end_price, amount in self.range_amount_list:
            if start_price <= price <= end_price:
                return amount
        return None

    def on_trade(self, datetime, price):
        predefined_amount = self._get_predefined_amount(price)
        if predefined_amount is None or predefined_amount == self.position.current_eth:
            return

        # sell
        if self.position.current_eth - predefined_amount > 0:
            if not self.trade_history:
                try:
                    self.position.sell(price, self.position.current_eth - predefined_amount)
                    self.trade_history.append((datetime, price, "S", price))
                except Exception as e:
                    print(e)
                    return
            else:
                current_range_upper = self.amount_range_dict[self.position.current_eth][1]
                new_range_upper = self.amount_range_dict[predefined_amount][1]
                for range_amount in self.range_amount_list:
                    range_start_price = range_amount[0]
                    if current_range_upper < range_start_price < new_range_upper:
                        try:
                            self.position.sell(range_start_price, self.trade_amount)
                            self.trade_history.append((datetime, price, "S", range_start_price))
                        except Exception as e:
                            print(e)
                            return
        # buy
        else:
            if not self.trade_history:
                try:
                    self.position.buy(price, predefined_amount - self.position.current_eth)
                    self.trade_history.append((datetime, price, "B", price))
                except Exception as e:
                    print(e)
                    return
            else:
                current_range_lower = self.amount_range_dict[self.position.current_eth][0]
                new_range_lower = self.amount_range_dict[predefined_amount][0]
                for range_amount in self.range_amount_list[::-1]:
                    range_end_price = range_amount[1]
                    if new_range_lower < range_end_price < current_range_lower:
                        try:
                            self.position.buy(range_end_price, self.trade_amount)
                            self.trade_history.append((datetime, price, "B", range_end_price))
                        except Exception as e:
                            print(e)
                            return
        print("date: ", datetime, "price: ", price, "trade_type:", self.trade_history[-1][2], "trade price:",
              self.trade_history[-1][3], self.position, "profit:", self.position.get_profit(price), "profit rate:",
              self.position.get_profit_rate(price))

        # print("init value: {}, current_value: {}, profit_rate: {}".format(self.position.get_init_value(price),
        #                                                                   self.position.get_current_value(price),
        #                                                                   self.position.get_profit_rate(price)))

    def main(self):
        print("init date:", self.data[0]["datetime"], "init price:", self.data[0]["price"], "init eth:",
              self.position.current_eth, "init usd:", self.position.current_usd)
        for item in self.data:
            self.on_trade(item["datetime"], item["price"])
        print("final date: ", self.data[-1]["datetime"], "price: ", self.data[-1]["price"], self.position, "profit:",
              self.position.get_profit(self.data[-1]["price"]), "profit rate:",
              self.position.get_profit_rate(self.data[-1]["price"]))


if __name__ == '__main__':
    # 如果赚的是 gap 钱，就需要多设在经常波动的区间
    trade_price_list = [1650, 1700, 1750, 1800, 1850, 1900, 1950, 2000]
    trade_gap = 10
    trade_amount = 0.25
    # best param until now, about 10% profit
    # trade_price_list = [1700, 1800, 1850, 1900, 2000]
    # trade_gap = 10
    # trade_amount = 0.5
    fee_rate = 0.0006
    pressure_support_dynamic_strategy = PressureSupportDynamicStrategy(trade_price_list, trade_gap, trade_amount,
                                                                       fee_rate, init_eth=1, init_usd=2000)
    pressure_support_dynamic_strategy.main()
