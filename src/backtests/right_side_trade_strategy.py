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


class RightSideTradeStrategy(object):

    def __init__(self, init_usd, init_eth, stage=5):
        self.position = Position(init_usd, init_eth)
        self.trade_amount = self.position.init_eth / stage
        self.exchange_data = self._init_exchange_data()
        self.trade_history = []

    @staticmethod
    def _init_exchange_data():
        cex_data = exchange_log_parser.parse_cex_data(BASE_PATH + "/logs/eth_socket_order.log.2023-06-15")
        cex_data += exchange_log_parser.parse_cex_data(BASE_PATH + "/logs/eth_socket_order.log.2023-06-16")

        dex_data = exchange_log_parser.parse_dex_data(BASE_PATH + "/logs/arb_price_storage.log.2023-06-15")
        dex_data += exchange_log_parser.parse_dex_data(BASE_PATH + "/logs/arb_price_storage.log.2023-06-16")
        # use dex data to find the corresponding cex data, and combine them
        combine_result = exchange_log_parser.combine_dex_cex(dex_data, cex_data, time_range=1)

        df = pd.DataFrame(combine_result)
        df["price_diff"] = df["cex_price"] - df["dex_price"]
        df["price_diff_in_tick"] = df["cex_price"].apply(math_utils.price_to_tick) - df["dex_price"].apply(
            math_utils.price_to_tick)
        df["cex_datetime"] = df["cex_time"].apply(utils.utc_timestamp_to_datetime_ms_str).str[:-4]
        df["dex_datetime"] = df["dex_time"].apply(utils.utc_timestamp_to_datetime_ms_str).str[:-4]
        return df.to_dict("records")

    def _is_tradeable(self, trade_type, trade_price):
        if trade_type in TradeType.BUY_LIST:
            return self.position.current_usd >= trade_price * self.trade_amount
        elif trade_type in TradeType.SELL_LIST:
            return self.position.current_eth >= self.trade_amount

    def _start_trade(self):
        for i, item in enumerate(self.exchange_data):
            if item["price_diff_in_tick"] >= 2:
                return i, Trade(TradeType.BUY, item["cex_time"], item["dex_price"], self.trade_amount)
            elif item["price_diff_in_tick"] < 0:
                return i, Trade(TradeType.SELL, item["cex_time"], item["dex_price"], self.trade_amount)

    def on_trade(self, trade):
        if trade.trade_type == TradeType.BUY:
            self.position.buy(trade.price, trade.amount)
        elif trade.trade_type == TradeType.SELL:
            self.position.sell(trade.price, trade.amount)
        self.trade_history.append(trade)

    def _is_continue_buy(self, previous_trade, exchange_item):
        if exchange_item["cex_price"] > exchange_item["dex_price"] and \
                math_utils.price_to_tick(exchange_item["dex_price"]) - previous_trade.price:
            return True

    def get_trade_type(self, previous_trade, exchange_last_item, exchange_item):
        if previous_trade in TradeType.BUY_LIST:


    def main(self):
        idx, trade = self._start_trade()
        previous_trade = trade
        for item in self.exchange_data[idx+1:]:

