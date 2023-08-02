import requests

from utils import utils


POLONIEX_URL = 'https://poloniex.com/public?command=returnChartData&currencyPair={}&start={}&end={}&period={}'
CRYPTOCOMPARE_URL = "https://min-api.cryptocompare.com/data/v2/histoday?fsym={}&tsym={}&limit=1000&toTs={}"


def get_pair_result_from_poloniex(pair, start_date, end_date, period=3600):
    start_ts = utils.date_to_utc_timestamp(start_date)
    current_ts = utils.date_to_utc_timestamp(end_date)
    result = []

    while start_ts < current_ts:
        print("processing date:", utils.utc_timestamp_to_date_str(start_ts))
        end_ts = start_ts + period * 480
        if period == 86400:
            end_ts = start_ts + period * 20

        current_data = requests.get(POLONIEX_URL.format(pair, start_ts, end_ts, period)).json()
        result += current_data

        start_ts = end_ts + period
    return result


def get_pair_result_from_cryptocompare(from_token, to_token, start_date, end_date):
    current_timestamp = utils.date_to_utc_timestamp(end_date)
    start_timestamp = utils.date_to_utc_timestamp(start_date)
    result = []
    while current_timestamp >= start_timestamp:
        print("Processing date: ", utils.utc_timestamp_to_date(current_timestamp))
        response = requests.get(CRYPTOCOMPARE_URL.format(from_token, to_token, current_timestamp))
        data = response.json()['Data']
        if not data:
            break
        for d in data['Data'][::-1]:
            if d["time"] >= start_timestamp:
                result.append(d)
            else:
                break
        current_timestamp = data['TimeFrom'] - 60

    return result[::-1]
