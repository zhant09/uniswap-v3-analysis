#!/usr/bin/env python3

#
# Example that shows the full range of the current liquidity distribution
# in the 0.3% USDC/ETH pool using data from the Uniswap v3 subgraph.
#

import argparse
import datetime
import logging
import math

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

from storage_helper import EthPoolInfo
from utils.db import db
from utils.utils import date_to_utc_timestamp
from utils.config import BASE_PATH


log_file = BASE_PATH + "/logs/" + datetime.datetime.now().strftime('liquidity_storage_%Y%m%d.log')
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(module)s %(levelname)s %(message)s')

# default pool id is the 0.3% USDC/ETH pool
# POOL_ID = "0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8"
# 0.05% WBTC/ETH pool
# POOL_ID = "0x4585fe77225b41b697c938b018e2ac67ac5a20c0"
# 0.3% WBTC/ETH pool
# POOL_ID = "0xcbcdf9626bc03e24f779434178a73a0b4bad62ed"

# if len(sys.argv) > 1:
#     POOL_ID = sys.argv[1]

TICK_BASE = 1.0001

client = Client(
    transport=RequestsHTTPTransport(
        url='https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3',
        verify=True,
        retries=5,
    ))


def tick_to_price(tick):
    return TICK_BASE ** tick


# Not all ticks can be initialized. Tick spacing is determined by the pool's fee tier.
def fee_tier_to_tick_spacing(fee_tier):
    return {
        100: 1,
        500: 10,
        3000: 60,
        10000: 200
    }.get(fee_tier, 60)


def get_pool_info(date, pool_id):
    # get pool info
    pool_query = """query get_pools($pool_id: ID!, $date: Int) {
        poolDayDatas(where: {pool: $pool_id, date: $date}) {
            tick
            pool {
                feeTier
                token0 {
                    symbol
                    decimals
                }
                token1 {
                    symbol
                    decimals
                }
            }
        }
    }"""

    ts = date_to_utc_timestamp(date)
    try:
        pool_info = EthPoolInfo(pool_id)

        variables = {"pool_id": pool_id, "date": ts}
        response = client.execute(gql(pool_query), variable_values=variables)

        if len(response['poolDayDatas']) == 0:
            logging.error("pool not found, pool_id: ", pool_id)
            exit(-1)

        pool_data = response['poolDayDatas'][0]
        pool_info.current_tick = int(pool_data["tick"])
        pool_info.fee_tier = int(pool_data["pool"]["feeTier"])
        pool_info.tick_spacing = fee_tier_to_tick_spacing(pool_info.fee_tier)

        pool_info.token0 = pool_data["pool"]["token0"]["symbol"]
        pool_info.token1 = pool_data["pool"]["token1"]["symbol"]
        pool_info.decimals0 = int(pool_data["pool"]["token0"]["decimals"])
        pool_info.decimals1 = int(pool_data["pool"]["token1"]["decimals"])
        return pool_info
    except Exception as ex:
        logging.error("got exception while querying pool data:", ex)
        exit(-1)


def get_tick_data(date, pool_info):
    tick_query = """query get_ticks($num_skip: Int, $pool_id: ID!, $date: Int) {
        tickDayDatas(skip:$num_skip, where: {pool: $pool_id, date: $date}) {
            date
            tick {
                tickIdx
                liquidityNet
            }
        }
    }"""

    # get tick info
    tick_mapping = {}
    num_skip = 0

    ts = date_to_utc_timestamp(date)
    try:
        while True:
            logging.info("Querying ticks, num_skip={}".format(num_skip))
            variables = {"num_skip": num_skip, "pool_id": pool_info.pool_id, "date": ts}
            response = client.execute(gql(tick_query), variable_values=variables)

            tick_data = response["tickDayDatas"]
            if len(tick_data) == 0:
                break
            num_skip += len(tick_data)
            for item in tick_data:
                tick_mapping[int(item["tick"]["tickIdx"])] = int(item["tick"]["liquidityNet"])
        return tick_mapping
    except Exception as ex:
        logging.error("got exception while querying tick data:", ex)
        exit(-1)


def get_liquidity_data(date, pool_info: EthPoolInfo, tick_mapping: dict):
    # Start from zero; if we were iterating from the current tick, would start from the pool's total liquidity
    liquidity = 0

    # Find the boundaries of the price range
    min_tick = min(tick_mapping.keys())
    max_tick = max(tick_mapping.keys())

    # Compute the tick range. This code would work as well in Python: `current_tick // tick_spacing * tick_spacing`
    # However, using floor() is more portable.
    current_range_bottom_tick = math.floor(pool_info.current_tick / pool_info.tick_spacing) * pool_info.tick_spacing

    # current_price = tick_to_price(pool_info.current_tick)
    # adjusted_current_price = current_price / (10 ** (pool_info.decimals1 - pool_info.decimals0))

    # Iterate over the tick map starting from the bottom
    tick = min_tick
    insert_data = []
    while tick <= max_tick:
        line_dict = {
            "pool_id": pool_info.pool_id,
            "chain": "ETH",
            "date": date,
            "fee_tier": pool_info.fee_tier,
            "tick_spacing": pool_info.tick_spacing,
            "token0": pool_info.token0,
            "token1": pool_info.token1,
            "decimals0": pool_info.decimals0,
            "decimals1": pool_info.decimals1
        }
        liquidity_delta = tick_mapping.get(tick, 0)
        liquidity += liquidity_delta

        bottom_tick = tick
        top_tick = bottom_tick + pool_info.tick_spacing

        bottom_price = tick_to_price(bottom_tick) / (10 ** (pool_info.decimals1 - pool_info.decimals0))
        top_price = tick_to_price(top_tick) / (10 ** (pool_info.decimals1 - pool_info.decimals0))

        line_dict["bottom_tick"] = bottom_tick
        line_dict["top_tick"] = top_tick
        line_dict["liquidity_net"] = liquidity_delta
        line_dict["liquidity"] = liquidity
        line_dict["bottom_price"] = bottom_price
        line_dict["top_price"] = top_price

        # Compute square roots of prices corresponding to the bottom and top ticks
        sa = tick_to_price(bottom_tick // 2)
        sb = tick_to_price(top_tick // 2)

        locked_amount0 = 0
        locked_amount1 = 0
        is_current_tick = 0
        if tick < current_range_bottom_tick:
            amount1 = liquidity * (sb - sa)
            locked_amount1 = amount1 / (10 ** pool_info.decimals1)
        elif tick == current_range_bottom_tick:
            current_sqrt_price = tick_to_price(pool_info.current_tick / 2)
            amount0 = liquidity * (sb - current_sqrt_price) / (current_sqrt_price * sb)
            amount1 = liquidity * (current_sqrt_price - sa)
            locked_amount0 = amount0 / (10 ** pool_info.decimals0)
            locked_amount1 = amount1 / (10 ** pool_info.decimals1)
            is_current_tick = 1
        else:
            # Compute the amounts of tokens potentially in the range
            amount1 = liquidity * (sb - sa)
            amount0 = amount1 / (sb * sa)
            locked_amount0 = amount0 / (10 ** pool_info.decimals0)

        line_dict["locked_amount0"] = locked_amount0
        line_dict["locked_amount1"] = locked_amount1
        line_dict["is_current_tick"] = is_current_tick
        insert_data.append(line_dict)

        tick += pool_info.tick_spacing

    return insert_data


def insert_into_db(insert_data):
    sql = """INSERT INTO `pool_liquidity` (`pool_id`, `chain`, `date`, `fee_tier`, `tick_spacing`, `token0`, `token1`,
        `decimals0`, `decimals1`, `bottom_tick`, `top_tick`, `liquidity_net`, `liquidity`, `bottom_price`, `top_price`,
        `locked_amount0`, `locked_amount1`, `is_current_tick`) VALUES (%(pool_id)s, %(chain)s, %(date)s, %(fee_tier)s,
         %(tick_spacing)s, %(token0)s, %(token1)s, %(decimals0)s, %(decimals1)s, %(bottom_tick)s, %(top_tick)s,
         %(liquidity_net)s, %(liquidity)s, %(bottom_price)s, %(top_price)s, %(locked_amount0)s, %(locked_amount1)s,
         %(is_current_tick)s) """
    insert_count = db.execute_many(sql, insert_data)[0]
    return insert_count


def main(pool_id, start_date, end_date):
    # iterate over dates
    date = start_date
    while date <= end_date:
        logging.info("Processing date: {}".format(date))
        pool_info = get_pool_info(date, pool_id)
        tick_mapping = get_tick_data(date, pool_info)
        insert_data = get_liquidity_data(date, pool_info, tick_mapping)
        insert_count = insert_into_db(insert_data)
        logging.info("Inserted {} rows".format(insert_count))
        date += datetime.timedelta(days=1)


if __name__ == "__main__":
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
