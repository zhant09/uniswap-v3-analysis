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

from storage_helper import PoolInfo
from utils.db import db
from utils.config import BASE_PATH


logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("gql").setLevel(logging.WARNING)
log_file = BASE_PATH + "/logs/" + datetime.datetime.now().strftime('liquidity_realtime_storage_%Y%m%d.log')
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(module)s %(levelname)s %(message)s')

TICK_BASE = 1.0001

client = Client(
    transport=RequestsHTTPTransport(
        url='https://api.thegraph.com/subgraphs/name/messari/uniswap-v3-arbitrum',
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


def get_pool_info(pool_id):
    # get pool info
    pool_query = """query get_pools($pool_id: ID!) {
        liquidityPool(id: $pool_id) {
            tick
            inputTokens {
                symbol
                decimals
            }
            fees {
                feeType
                feePercentage
            }
        }
    }"""

    try:
        logging.info("Querying pool meta data")

        pool_info = PoolInfo(pool_id)
        variables = {"pool_id": pool_id}
        response = client.execute(gql(pool_query), variable_values=variables)

        if len(response['liquidityPool']) == 0:
            logging.error("pool not found, pool_id: ", pool_id)
            exit(-1)

        pool_data = response['liquidityPool']
        pool_info.current_tick = int(pool_data["tick"])
        for fee_pair in pool_data["fees"]:
            if fee_pair["feeType"] == "FIXED_TRADING_FEE":
                pool_info.fee_tier = int(10 ** 4 * float(fee_pair["feePercentage"]))  # convert to a million base
        pool_info.tick_spacing = fee_tier_to_tick_spacing(pool_info.fee_tier)

        pool_info.token0 = pool_data["inputTokens"][0]["symbol"]
        pool_info.token1 = pool_data["inputTokens"][1]["symbol"]
        pool_info.decimals0 = int(pool_data["inputTokens"][0]["decimals"])
        pool_info.decimals1 = int(pool_data["inputTokens"][1]["decimals"])
        return pool_info
    except Exception as ex:
        logging.error("got exception while querying pool data:", ex)
        exit(-1)


def get_tick_data(pool_info):
    tick_query = """query get_ticks($num_skip: Int, $pool_id: ID!) {
        ticks(skip: $num_skip, where: {pool: $pool_id}) {
            index
            liquidityNet
        }
    }"""

    # get tick info
    tick_mapping = {}
    num_skip = 0

    error_times = 0
    while True:
        logging.info("Querying ticks, num_skip={}".format(num_skip))
        variables = {"num_skip": num_skip, "pool_id": pool_info.pool_id}
        try:
            response = client.execute(gql(tick_query), variable_values=variables)

            tick_data = response["ticks"]
            if len(tick_data) == 0:
                break
            num_skip += len(tick_data)
            for item in tick_data:
                tick_mapping[int(item["index"])] = int(item["liquidityNet"])
        except Exception as ex:
            error_times += 1
            if error_times == 3:
                logging.error("got 3 times exception while querying tick data, exit.", ex)
                exit(-1)
            logging.info("retrying... num_skip={}, error_times={}".format(num_skip, error_times))
    return tick_mapping


def get_liquidity_data(dt: datetime, pool_info: PoolInfo, tick_mapping: dict):
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
            "chain": "ARB",
            "datetime": dt,
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
    sql = """INSERT INTO `pool_liquidity` (`pool_id`, `chain`, `datetime`, `fee_tier`, `tick_spacing`, `token0`, 
        `token1`, `decimals0`, `decimals1`, `bottom_tick`, `top_tick`, `liquidity_net`, `liquidity`, `bottom_price`, 
        `top_price`, `locked_amount0`, `locked_amount1`, `is_current_tick`) VALUES (%(pool_id)s, %(chain)s, 
        %(datetime)s, %(fee_tier)s, %(tick_spacing)s, %(token0)s, %(token1)s, %(decimals0)s, %(decimals1)s, 
        %(bottom_tick)s, %(top_tick)s, %(liquidity_net)s, %(liquidity)s, %(bottom_price)s, %(top_price)s, 
        %(locked_amount0)s, %(locked_amount1)s, %(is_current_tick)s) """
    insert_count = db.execute_many(sql, insert_data)[0]
    return insert_count


def filter_data(insert_data, token0_limit, token1_limit):
    logging.info("Filtering data, before filter: {} rows".format(len(insert_data)))
    remain_data = []
    for item in insert_data:
        if item["locked_amount0"] > token0_limit or item["locked_amount1"] > token1_limit:
            remain_data.append(item)
    logging.info("Filtering data, after filter: {} rows".format(len(remain_data)))
    return remain_data


def main(pool_id, token0_amount_filter, token1_amount_filter):
    dt = datetime.datetime.now()
    logging.info("Processing ARB pool {} at {}".format(pool_id, dt))

    pool_info = get_pool_info(pool_id)
    tick_mapping = get_tick_data(pool_info)
    insert_data = get_liquidity_data(dt, pool_info, tick_mapping)
    insert_data = filter_data(insert_data, token0_amount_filter, token1_amount_filter)
    insert_count = insert_into_db(insert_data)
    logging.info("Inserted {} rows".format(insert_count))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pool_id",
        type=str,
        required=True
    )
    parser.add_argument(
        '--token0_amount_filter',
        type=float,
        default=0.0
    )
    parser.add_argument(
        '--token1_amount_filter',
        type=float,
        default=0.0
    )

    args = parser.parse_args()
    main(args.pool_id, args.token0_amount_filter, args.token1_amount_filter)
