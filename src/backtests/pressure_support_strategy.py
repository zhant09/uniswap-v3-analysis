import copy

from data_parser import price_data_parser
from utils.config import BASE_PATH
from entity.position import Position
from evaluation import sharpe_ratio


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

        is_trade = False
        # sell
        sell_price_list = self.trade_price_dict["sell"]
        for sell_price, amount_mpl in sell_price_list:
            if price < sell_price or (last_trade is not None and last_trade[1] >= sell_price):
                continue

            if self._on_sell(datetime, sell_price, self.trade_amount * amount_mpl) is not False:
                is_trade = True
                print("date: ", datetime, "price: ", price, "trade_type:", self.trade_history[-1][3], "trade price:",
                      self.trade_history[-1][1], self.position, "profit:", self.position.get_profit(price),
                      "profit rate:", self.position.get_profit_rate(price))

            if last_trade is None:
                break  # only sell once

        if is_trade:
            return is_trade

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
                break  # only sell once

        return is_trade

    def _calc_origin_daily_return(self, today_price, yesterday_price):
        yesterday_value = self.position.get_init_value(yesterday_price)
        today_value = self.position.get_init_value(today_price)
        daily_profit = today_value - yesterday_value
        daily_return = daily_profit / yesterday_value
        return daily_return

    def _calc_daily_return(self, yesterday_position, today_price, yesterday_price):
        yesterday_value = yesterday_position.get_value(yesterday_price)
        today_value = self.position.get_value(today_price)
        daily_profit = today_value - yesterday_value
        daily_return = daily_profit / yesterday_value
        return daily_return

    def main(self):
        first_price = self.data[0]["price"]
        print("init date:", self.data[0]["datetime"], "init price:", first_price, "init eth:",
              self.position.current_eth, "init usd:", self.position.current_usd)

        end_time = "23:00:00"
        origin_daily_return_list = []
        daily_return_list = []
        yesterday_position = copy.deepcopy(self.position)
        yesterday_price = first_price
        for item in self.data:
            date_time = item["datetime"]
            price = item["price"]
            self.on_trade(date_time, price)

            day_list = date_time.split(" ")
            day = day_list[0]
            day_time = day_list[1]
            if day_time[:-4] == end_time:
                origin_daily_return = self._calc_origin_daily_return(price, yesterday_price)
                origin_daily_return_list.append(origin_daily_return)

                daily_return = self._calc_daily_return(yesterday_position, price, yesterday_price)
                daily_return_list.append(daily_return)
                yesterday_position = copy.deepcopy(self.position)
                yesterday_price = price

                # print("date: ", day, "price: ", price, "origin daily return:", origin_daily_return,
                #       "daily return:", daily_return, "strategy profit rate:", self.position.get_profit_rate(price))

        last_price = self.data[-1]["price"]
        origin_profit = self.position.get_init_value(last_price) - self.position.get_init_value(first_price)
        origin_profit_rate = origin_profit / self.position.get_init_value(first_price)

        strategy_profit = self.position.get_profit(last_price)
        strategy_profit_rate = self.position.get_profit_rate(last_price)

        overall_profit = origin_profit + strategy_profit
        overall_profit_rate = overall_profit / self.position.get_init_value(first_price)
        print("final date: ", self.data[-1]["datetime"], "price: ", last_price, self.position)
        print("origin profit:", origin_profit, "origin profit rate:", origin_profit_rate, "strategy profit:",
              strategy_profit, "strategy profit rate:", strategy_profit_rate, "overall profit:", overall_profit,
              "overall profit rate:", overall_profit_rate)

        rf = 0.0365 / 365
        origin_sharpe_ratio = sharpe_ratio.calc(origin_daily_return_list, rf)
        overall_sharpe_ratio = sharpe_ratio.calc(daily_return_list, rf)
        print("origin sharpe ratio:", origin_sharpe_ratio, "sharpe ratio:", overall_sharpe_ratio)


if __name__ == '__main__':
    # best param until now, about 18.5% profit
    # init_eth = 1
    # init_usd = 1000
    # trade_amount = 0.25
    # trade_price_dict = {"buy": [(1800, 1), (1750, 1), (1700, 2), (1650, 2)],
    #                     "sell": [(1900, 1), (1950, 1), (2000, 2), (2100, 2)]}
    init_eth = 1
    init_usd = 1000
    trade_amount = 0.25
    trade_price_dict = {"buy": [(1750, 2), (1700, 2), (1650, 2)],
                        "sell": [(1950, 2), (2000, 2), (2100, 2)]}
    # trade_price_dict = {"buy": [(1800, 1), (1750, 1), (1700, 2), (1650, 2)],
    #                     "sell": [(1900, 1), (1950, 1), (2000, 2), (2100, 2)]}
    fee_rate = 0.0006
    pressure_support_strategy = PressureSupportStrategy(trade_price_dict, init_eth, init_usd, trade_amount, fee_rate)
    pressure_support_strategy.main()
    # pressure_support_strategy1 = PressureSupportStrategy(trade_price_dict, init_eth, init_usd, trade_amount, fee_rate,
    #                                                     is_train=True)
    # pressure_support_strategy1.main()

    # pressure_support_strategy2 = PressureSupportStrategy(trade_price_dict, init_eth, init_usd, trade_amount, fee_rate,
    #                                                     is_test=True)
    # pressure_support_strategy2.main()
