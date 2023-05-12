#!/usr/bin/env python3

#
# Example that shows the full range of the current liquidity distribution
# in the 0.3% USDC/ETH pool using data from the Uniswap v3 subgraph.
#

import datetime
import logging
import math
import os
import sys

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

from storage_helper import EthPoolInfo


BASE_PATH = os.path.abspath(os.path.join(os.getcwd(), ".."))

log_file = BASE_PATH + "/logs/" + datetime.datetime.now().strftime('liquidity_storage_%Y%m%d.log')
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(module)s %(levelname)s %(message)s')

# default pool id is the 0.3% USDC/ETH pool
# POOL_ID = "0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8"
# 0.05% WBTC/ETH pool
# POOL_ID = "0x4585fe77225b41b697c938b018e2ac67ac5a20c0"
# 0.3% WBTC/ETH pool
# POOL_ID = "0xcbcdf9626bc03e24f779434178a73a0b4bad62ed"

if len(sys.argv) > 1:
    POOL_ID = sys.argv[1]

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


def get_pool_info():
    # get pool info
    pool_query = """query get_pools($pool_id: ID!) {
        pools(where: {id: $pool_id}) {
            tick
            sqrtPrice
            liquidity
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
    }"""
    try:
        variables = {"pool_id": POOL_ID}
        response = client.execute(gql(pool_query), variable_values=variables)

        if len(response['pools']) == 0:
            logging.error("pool not found")
            exit(-1)

        pool_info = EthPoolInfo(POOL_ID)

        pool = response['pools'][0]
        pool_info.current_tick = int(pool["tick"])
        pool_info.fee_tier = int(pool["feeTier"])
        pool_info.tick_spacing = fee_tier_to_tick_spacing(pool_info.fee_tier)

        pool_info.token0 = pool["token0"]["symbol"]
        pool_info.token1 = pool["token1"]["symbol"]
        pool_info.decimals0 = int(pool["token0"]["decimals"])
        pool_info.decimals1 = int(pool["token1"]["decimals"])
        return pool_info
    except Exception as ex:
        logging.error("got exception while querying pool data:", ex)
        exit(-1)


def get_tick_data():
    tick_query = """query get_ticks($date: Int, $num_skip: Int, $pool_id: ID!) {
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
    try:
        while True:
            logging.info("Querying ticks, num_skip={}".format(num_skip))
            variables = {"num_skip": num_skip, "pool_id": POOL_ID}
            response = client.execute(gql(tick_query), variable_values=variables)

            if len(response["ticks"]) == 0:
                break
            num_skip += len(response["ticks"])
            for item in response["ticks"]:
                tick_mapping[int(item["tickIdx"])] = int(item["liquidityNet"])
        return tick_mapping
    except Exception as ex:
        logging.error("got exception while querying tick data:", ex)
        exit(-1)


def liquidity_calculation(pool_info, tick_mapping):
    # Start from zero; if we were iterating from the current tick, would start from the pool's total liquidity
    liquidity = 0

    # Find the boundaries of the price range
    min_tick = min(tick_mapping.keys())
    max_tick = max(tick_mapping.keys())

    # Compute the tick range. This code would work as well in Python: `current_tick // tick_spacing * tick_spacing`
    # However, using floor() is more portable.
    current_range_bottom_tick = math.floor(pool_info.current_tick / pool_info.tick_spacing) * pool_info.tick_spacing

    current_price = tick_to_price(pool_info.current_tick)
    adjusted_current_price = current_price / (10 ** (pool_info.decimals1 - pool_info.decimals0))

    # Sum up all tokens in the pool
    # total_amount0 = 0
    # total_amount1 = 0

    # Guess the preferred way to display the price;
    # try to print most assets in terms of USD;
    # if that fails, try to use the price value that's above 1.0 when adjusted for decimals.
    # stablecoins = ["USDC", "DAI", "USDT", "TUSD", "LUSD", "BUSD", "GUSD", "UST"]
    # if pool_info.token0 in stablecoins and pool_info.token1 not in stablecoins:
    #     invert_price = True
    # elif adjusted_current_price < 1.0:
    #     invert_price = True
    # else:
    #     invert_price = False

    # Iterate over the tick map starting from the bottom
    tick = min_tick
    while tick <= max_tick:
        liquidity_delta = tick_mapping.get(tick, 0)
        liquidity += liquidity_delta

        bottom_tick = tick
        top_tick = bottom_tick + pool_info.tick_spacing

        bottom_price = tick_to_price(bottom_tick) / (10 ** (pool_info.decimals1 - pool_info.decimals0))
        top_price = tick_to_price(top_tick) / (10 ** (pool_info.decimals1 - pool_info.decimals0))

        # inverted_price = 1 / adjusted_price
        # if invert_price:
        #     adjusted_price = 1 / adjusted_price
        #     tokens = "{} for {}".format(pool_info.token0, pool_info.token1)
        # else:
        #     tokens = "{} for {}".format(pool_info.token1, pool_info.token0)

        # should_print_tick = liquidity != 0
        # if should_print_tick:
        #     print("ticks=[{}, {}], bottom tick price={:.6f} {}".format(tick, tick + tick_spacing, adjusted_price, tokens))

        # Compute square roots of prices corresponding to the bottom and top ticks
        sa = tick_to_price(bottom_tick // 2)
        sb = tick_to_price(top_tick // 2)

        locked_amount0 = 0
        locked_amount1 = 0
        is_current_tick = 0
        if tick < current_range_bottom_tick:
            # Compute the amounts of tokens potentially in the range
            # Only token1 locked
            amount1 = liquidity * (sb - sa)
            locked_amount1 = amount1 / (10 ** pool_info.decimals1)

            # amount0 = amount1 / (sb * sa)
            # total_amount1 += amount1

            # if should_print_tick:
            #     locked_amount0 = amount0 / (10 ** decimals0)
            #     locked_amount1 = amount1 / (10 ** decimals1)
            #     print("        {:.2f} {} locked, potentially worth {:.2f} {}".format(locked_amount1, token1, locked_amount0, token0))

        elif tick == current_range_bottom_tick:
            # Always print the current tick. It normally has both assets locked
            # print("        Current tick, both assets present!")
            # print("        Current price={:.6f} {}".format(1 / adjusted_current_price if invert_price else adjusted_current_price, tokens))

            # Print the real amounts of the two assets needed to be swapped to move out of the current tick range
            current_sqrt_price = tick_to_price(pool_info.current_tick / 2)
            amount0 = liquidity * (sb - current_sqrt_price) / (current_sqrt_price * sb)
            amount1 = liquidity * (current_sqrt_price - sa)
            locked_amount0 = amount0 / (10 ** pool_info.decimals0)
            locked_amount1 = amount1 / (10 ** pool_info.decimals1)
            is_current_tick = 1

            # total_amount0 += amount0
            # total_amount1 += amount1

            # print("        {:.2f} {} and {:.2f} {} remaining in the current tick range".format(
            #     locked_amount0, token0, locked_amount1, token1))


        else:
            # Compute the amounts of tokens potentially in the range
            amount1 = liquidity * (sb - sa)
            amount0 = amount1 / (sb * sa)

            # Only token0 locked
            # total_amount0 += amount0

            locked_amount0 = amount0 / (10 ** pool_info.decimals0)
            # locked_amount1 = amount1 / (10 ** pool_info.decimals1)

            # if should_print_tick:
            #     locked_amount0 = amount0 / (10 ** decimals0)
            #     locked_amount1 = amount1 / (10 ** decimals1)
            #     print("        {:.2f} {} locked, potentially worth {:.2f} {}".format(locked_amount0, token0, locked_amount1, token1))

        tick += pool_info.tick_spacing


# print("In total: {:.2f} {} and {:.2f} {}".format(
#     total_amount0 / 10 ** decimals0, token0, total_amount1 / 10 ** decimals1, token1))
