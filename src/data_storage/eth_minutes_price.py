import argparse
import datetime
import logging
import requests

from utils.config import BASE_PATH
from utils.db import db
from utils import utils


log_file = BASE_PATH + "/logs/" + datetime.datetime.now().strftime('eth_minutes_price_%Y%m%d.log')
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(module)s %(levelname)s %(message)s')


KUCOIN_URL = "https://min-api.cryptocompare.com/data/v2/histominute?fsym=ETH&tsym=USD&limit=1000&toTs={}"


def get_start_timestamp():
    sql = "SELECT MAX(`time`) FROM `eth_minutes_price`"
    cnt, result = db.execute_one(sql)
    return result[0][0]


def insert_into_db(insert_data):
    sql = """INSERT INTO `eth_minutes_price` (`time`, `high`, `low`, `open`, `close`, `volume_from`, `volume_to`, 
        `conversion_type`, `conversion_symbol`) VALUES (%(time)s, %(high)s, %(low)s, %(open)s, %(close)s, 
        %(volumefrom)s, %(volumeto)s, %(conversionType)s, %(conversionSymbol)s)"""
    insert_count = db.execute_many(sql, insert_data)[0]
    return insert_count


def main(end_date):
    start_timestamp = get_start_timestamp()
    end_timestamp = utils.date_to_utc_timestamp(end_date)
    logging.info("Start processing, start timestamp: {}, end timestamp: {}".format(start_timestamp, end_timestamp))

    current_timestamp = end_timestamp
    kucoin_result = []
    while current_timestamp > start_timestamp:
        logging.info("Start processing, current time: {}".format(utils.utc_timestamp_to_datetime_str(current_timestamp)))
        response = requests.get(KUCOIN_URL.format(current_timestamp))
        kucoin_data = response.json()['Data']
        if not kucoin_data:
            break
        for d in kucoin_data['Data'][::-1]:
            if d["time"] > start_timestamp:
                kucoin_result.append(d)
            else:
                break
        current_timestamp = kucoin_data['TimeFrom'] - 60

    kucoin_result = kucoin_result[::-1]
    insert_count = insert_into_db(kucoin_result)
    logging.info("Insert {} records into db".format(insert_count))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--end_date",
        type=str,
        required=True,
    )

    args = parser.parse_args()
    end_date = datetime.datetime.strptime(args.end_date, "%Y-%m-%d")
    main(end_date)
