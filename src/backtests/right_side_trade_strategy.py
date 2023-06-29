import pandas as pd

from data_parser import exchange_log_parser
from utils import utils, math_utils
from utils.config import BASE_PATH
from position import Position
from trade import Trade, TradeType

"""
Strategy:
   Four possible status: continue_buy, continue sell，reverse_buy, reverse_sell
       continue_buy: dex_price > previous_dex_buy_price(10 ticks) and cex_price > dex_price
       continue_sell: dex_price < previous_dex_sell_price(10 ticks) and cex_price < dex_price
       reverse_buy: after continue_sell, cex_price - dex_price >= 2 ticks, for two continues
       reverse_sell: after continue_buy, cex_price - dex_price <= -2 ticks, for two continues
"""


def _is_buy(trade_type):
    if trade_type in [TradeType.BUY, TradeType.CONTINUE_BUY, TradeType.REVERSE_BUY]:
        return True
    return False


class RightSideTradeStrategy(object):

    def __init__(self, init_usd, init_eth, stage=5):
        self.position = Position(init_eth, init_usd)
        self.trade_amount = self.position.init_eth / stage
        self.exchange_data = self._init_exchange_data()
        self.trade_history = []

    @staticmethod
    def _init_exchange_data():
        print("reading cex data")
        cex_data = exchange_log_parser.parse_cex_data(BASE_PATH + "/logs/eth_socket_order.log.2023-06-15")
        cex_data += exchange_log_parser.parse_cex_data(BASE_PATH + "/logs/eth_socket_order.log.2023-06-16")

        print("reading dex data")
        dex_data = exchange_log_parser.parse_dex_data(BASE_PATH + "/logs/arb_price_storage.log.2023-06-15")
        dex_data += exchange_log_parser.parse_dex_data(BASE_PATH + "/logs/arb_price_storage.log.2023-06-16")

        print("combine cex & dex data")
        # use dex data to find the corresponding cex data, and combine them
        combine_result = exchange_log_parser.combine_dex_cex(dex_data, cex_data, time_range=1)

        df = pd.DataFrame(combine_result)
        df["price_diff"] = df["cex_price"] - df["dex_price"]
        df["price_diff_in_tick"] = df["cex_price"].apply(math_utils.price_to_tick) - df["dex_price"].apply(
            math_utils.price_to_tick)
        df["cex_datetime"] = df["cex_time"].apply(utils.utc_timestamp_to_datetime_ms_str).str[:-4]
        df["dex_datetime"] = df["dex_time"].apply(utils.utc_timestamp_to_datetime_ms_str).str[:-4]
        return df.to_dict("records")

    def _is_legal_trade(self, trade_type, trade_price):
        if _is_buy(trade_type):
            return self.position.current_usd >= trade_price * self.trade_amount
        return self.position.current_eth >= self.trade_amount

    def _start_trade(self):
        for i, item in enumerate(self.exchange_data):
            if item["price_diff_in_tick"] >= 2:
                return i, Trade(TradeType.BUY, item["cex_time"], item["dex_price"], self.trade_amount)
            elif item["price_diff_in_tick"] < 0:
                return i, Trade(TradeType.SELL, item["cex_time"], item["dex_price"], self.trade_amount)

    # todo: 当前未考虑交易摩擦
    def on_trade(self, trade):
        if _is_buy(trade.trade_type):
            self.position.buy(trade.price, trade.amount)
        else:
            self.position.sell(trade.price, trade.amount)
        self.trade_history.append(trade)

    # def _is_continue_buy(self, exchange_item):
    #     previous_trade = self.trade_history[-1]
    #     if _is_buy(previous_trade.trade_type) and exchange_item["price_diff_in_tick"] > 0 and \
    #             math_utils.price_to_tick(exchange_item["dex_price"]) - previous_trade.tick >= 10:
    #         return True
    #     return False
    #
    # def _is_continue_sell(self, exchange_item):
    #     previous_trade = self.trade_history[-1]
    #     if (not _is_buy(previous_trade.trade_type)) and exchange_item["price_diff_in_tick"] < 0 and \
    #             math_utils.price_to_tick(exchange_item["dex_price"]) - previous_trade.tick <= -10:
    #         return True
    #     return False

    def _is_to_buy(self, exchange_item, last_exchange_item):
        previous_trade = self.trade_history[-1]
        if exchange_item["price_diff_in_tick"] > 2 and last_exchange_item["price_diff_in_tick"] > 2 and \
                abs(math_utils.price_to_tick(exchange_item["dex_price"]) - previous_trade.tick) > 10:
            return True
        return False

    def _is_to_sell(self, exchange_item, last_exchange_item):
        previous_trade = self.trade_history[-1]
        if exchange_item["price_diff_in_tick"] < -2 and last_exchange_item["price_diff_in_tick"] < -2 and \
                abs(math_utils.price_to_tick(exchange_item["dex_price"]) - previous_trade.tick) > 10:
            return True
        return False

    def _get_item_trade_type(self, exchange_item, exchange_last_item):
        if self._is_to_buy(exchange_item, exchange_last_item):
            return TradeType.BUY
        elif self._is_to_sell(exchange_item, exchange_last_item):
            return TradeType.SELL
        # elif self._is_reverse_buy(exchange_item, exchange_last_item):
        #     return TradeType.REVERSE_BUY
        # elif self._is_reverse_sell(exchange_item, exchange_last_item):
        #     return TradeType.REVERSE_SELL
        return None

    def main(self):
        # print("init position: ", self.position)
        idx, trade = self._start_trade()
        self.on_trade(trade)
        for i, item in enumerate(self.exchange_data[idx + 2:]):
            trade_type = self._get_item_trade_type(item, self.exchange_data[idx + 1 + i])
            if trade_type is None:
                continue
            if not self._is_legal_trade(trade_type, item["dex_price"]):
                print("not enough money to trade")
                continue
            trade = Trade(trade_type, item["cex_time"], item["dex_price"], self.trade_amount)
            self.on_trade(trade)
            # print("trade_time: {}, trade_type: {}, trade_price: {}, profit: {}".format(item["cex_datetime"],
            #                                                                            trade_type.name,
            #                                                                            item["dex_price"],
            #                                                                            self.position.get_profit(item["dex_price"])))
        return self.trade_history


# if __name__ == '__main__':
#     init_usd = 200000
#     init_eth = 100
#     right_side_trader = RightSideTradeStrategy(init_usd, init_eth, stage=50)
#     right_side_trader.main()
