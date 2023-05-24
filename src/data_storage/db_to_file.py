import argparse
import datetime
import logging
import pandas as pd

from utils.db import db
from utils.config import BASE_PATH


log_file = BASE_PATH + "/logs/" + datetime.datetime.now().strftime('db_to_file_%Y%m%d.log')
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(module)s %(levelname)s %(message)s')


def get_data_from_db(pool_id, start_date, end_date):
    sql = """
    SELECT 
        `pool_id`, `chain`, `datetime`, `fee_tier`, `tick_spacing`, `token0`, `token1`, `decimals0`, `decimals1`, 
        `bottom_tick`, `top_tick`, `liquidity_net`, `liquidity`, `bottom_price`, `top_price`, `locked_amount0`, 
        `locked_amount1`, `is_current_tick` 
    FROM 
        `pool_liquidity` 
    WHERE 
        `pool_id` = "{}" AND `datetime` > "{}" AND `datetime` < "{}"  
    """.format(pool_id, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    data = db.execute_one(sql)[1]
    return data


def save_data_into_file(pool_id, date, data):
    columns = ["pool_id", "chain", "datetime", "fee_tier", "tick_spacing", "token0", "token1", "decimals0", "decimals1",
               "bottom_tick", "top_tick", "liquidity_net", "liquidity", "bottom_price", "top_price", "locked_amount0",
               "locked_amount1", "is_current_tick"]

    result = []
    for line_data in data:
        line_dict = dict()
        for i, d in enumerate(line_data):
            line_dict[columns[i]] = d
        result.append(line_dict)

    filename = BASE_PATH + "/data/pool_liquidity_{}_{}.csv.gzip".format(pool_id, date.strftime("%Y%m%d"))
    df = pd.DataFrame(result)
    df.to_csv(filename, compression="gzip", index=False)
    logging.info("Finishing saving data into file: {}".format(filename))


def main(pool_id, start_date, end_date):
    date = start_date
    while date <= end_date:
        logging.info("Processing Pool {} at {}".format(pool_id, date.strftime("%Y-%m-%d")))
        data = get_data_from_db(pool_id, date, date + datetime.timedelta(days=1))
        logging.info("Finishing Fetching data from db.")
        save_data_into_file(pool_id, date, data)
        date = date + datetime.timedelta(days=1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pool_id",
        type=str,
        required=True
    )
    parser.add_argument(
        "--start_date",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--end_date",
        type=str,
        required=True,
    )

    args = parser.parse_args()
    start_date = datetime.datetime.strptime(args.start_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(args.end_date, "%Y-%m-%d")
    main(args.pool_id, start_date, end_date)
