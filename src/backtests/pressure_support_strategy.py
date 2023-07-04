import copy

from data_parser import price_data_parser
from utils.config import BASE_PATH
from position import Position


class PressureSupportStrategy(object):

    # FILE_PATH = BASE_PATH + "/data/eth_usd_20230628.csv"
    FILE_PATH = BASE_PATH + "/data/eth_usd_polygon_20230703.csv"

    def __init__(self, trade_price_dict, init_eth, init_usd, trade_amount, fee_rate, is_train=False, is_test=False):
        self.trade_price_dict = trade_price_dict
        self.trade_amount = trade_amount
        self.fee_rate = fee_rate
        self._init_data(is_train, is_test)
        self.position = Position(init_eth, init_usd, self.fee_rate)
        self.trade_history = []  # (datetime, price, amount, "S"/"B")

    def _init_data(self, is_train, is_test):
        if is_train:
            self.data = price_data_parser.parse_polygon_data(self.FILE_PATH, "2023-03-21", "2023-05-23")
        elif is_test:
            self.data = price_data_parser.parse_polygon_data(self.FILE_PATH, "2023-05-23")
        else:
            self.data = price_data_parser.parse_polygon_data(self.FILE_PATH, "2023-03-21")

    def _on_sell(self, datetime, sell_price, amount):
        try:
            self.position.sell(sell_price, amount)
            self.trade_history.append((datetime, sell_price, amount, "S"))
        except Exception as e:
            print(datetime, e)
            return False

    def _on_buy(self, datetime, buy_price, amount):
        try:
            self.position.buy(buy_price, amount)
            self.trade_history.append((datetime, buy_price, amount, "B"))
        except Exception as e:
            print(datetime, e)
            return False

    def on_trade(self, datetime, price):
        last_trade = self.trade_history[-1] if self.trade_history else None

        # sell
        sell_price_list = self.trade_price_dict["sell"]
        for sell_price, amount_mpl in sell_price_list:
            if price < sell_price or (last_trade is not None and last_trade[1] >= sell_price):
                continue

            if self._on_sell(datetime, sell_price, self.trade_amount * amount_mpl) is not False:
                print("date: ", datetime, "price: ", price, "trade_type:", self.trade_history[-1][3], "trade price:",
                      self.trade_history[-1][1], self.position, "profit:", self.position.get_profit(price),
                      "profit rate:", self.position.get_profit_rate(price))
            if last_trade is None:
                return  # only sell once

        # buy
        buy_price_list = self.trade_price_dict["buy"]
        for buy_price, amount_mpl in buy_price_list:
            if price > buy_price or (last_trade is not None and last_trade[1] <= buy_price):
                continue

            if self._on_buy(datetime, buy_price, self.trade_amount * amount_mpl) is not False:
                print("date: ", datetime, "price: ", price, "trade_type:", self.trade_history[-1][3], "trade price:",
                      self.trade_history[-1][1], self.position, "profit:", self.position.get_profit(price),
                      "profit rate:", self.position.get_profit_rate(price))
            if last_trade is None:
                return  # only sell once

    def main(self):
        print("init date:", self.data[0]["datetime"], "init price:", self.data[0]["price"], "init eth:",
              self.position.current_eth, "init usd:", self.position.current_usd)
        for item in self.data:
            self.on_trade(item["datetime"], item["price"])
        print("final date: ", self.data[-1]["datetime"], "price: ", self.data[-1]["price"], self.position, "profit:",
              self.position.get_profit(self.data[-1]["price"]), "profit rate:",
              self.position.get_profit_rate(self.data[-1]["price"]))


if __name__ == '__main__':
    trade_price_dict = {"buy": [(1800, 1), (1750, 1), (1700, 2), (1650, 2)],
                        "sell": [(1900, 1), (1950, 1), (2000, 2), (2100, 2)]}
    # best param until now, about 18.5% profit
    # init_eth = 1
    # init_usd = 1000
    # trade_amount = 0.25
    init_eth = 1
    init_usd = 1000
    trade_amount = 0.25
    fee_rate = 0.0006
    # pressure_support_strategy1 = PressureSupportStrategy(trade_price_dict, init_eth, init_usd, trade_amount, fee_rate,
    #                                                     is_train=True)
    # pressure_support_strategy1.main()

    pressure_support_strategy2 = PressureSupportStrategy(trade_price_dict, init_eth, init_usd, trade_amount, fee_rate,
                                                        is_test=True)
    pressure_support_strategy2.main()
