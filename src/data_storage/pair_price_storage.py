import requests

from utils import utils


PRICE_URL = 'https://poloniex.com/public?command=returnChartData&currencyPair={}&start={}&end={}&period={}'


def get_pair_result(pair, start_date, end_date, period=3600):
    start_ts = utils.date_to_utc_timestamp(start_date)
    current_ts = utils.date_to_utc_timestamp(end_date)
    result_data = []

    while start_ts < current_ts:
        end_ts = start_ts + period * 480
        if period == 86400:
            end_ts = start_ts + period * 20

        current_data = requests.get(PRICE_URL.format(pair, start_ts, end_ts, period)).json()
        result_data += current_data

        start_ts = end_ts + period
        print(utils.utc_timestamp_to_date_str(start_ts))
    return result_data
