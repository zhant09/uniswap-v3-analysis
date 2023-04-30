#!/usr/bin/env python3

#
# Example that shows the full range of the current liquidity distribution
# in the 0.3% USDC/ETH pool using data from the Arbitrum Uniswap v3 subgraph.
#

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import math
import sys


# 0.05% Arbitrum chain USDC/ETH pool
POOL_ID = "0xc31e54c7a869b9fcbecc14363cf510d1c41fa443"
# 0.3% Arbitrum chain USDC/ETH pool
# POOL_ID = "0x17c14d2c404d167802b16c450d3c99f88f2c4f4d"

# if passed in command line, use an alternative pool ID
if len(sys.argv) > 1:
    POOL_ID = sys.argv[1]

TICK_BASE = 1.0001

pool_query = """query get_pools($pool_id: ID!) {
  liquidityPool(id: $pool_id) {
    tick
    totalLiquidity
    totalValueLockedUSD
    fees {
        feeType
        feePercentage
    }
  }
}"""

tick_query = """query get_ticks($num_skip: Int, $pool_id: ID!) {
  ticks(skip: $num_skip, where: {pool: $pool_id}) {
    index
    liquidityNet
  }
}"""


def tick_to_price(tick):
    return TICK_BASE ** tick


def adjust_price(p):
    return p * 1e12


# Not all ticks can be initialized. Tick spacing is determined by the pool's fee tier.
def fee_tier_to_tick_spacing(fee_tier):
    return {
        "0.01": 1,
        "0.05": 10,
        "0.3": 60,
        "1": 200
    }.get(fee_tier)


client = Client(
    transport=RequestsHTTPTransport(
        # url='https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3',
        url='https://api.thegraph.com/subgraphs/name/messari/uniswap-v3-arbitrum',
        verify=True,
        retries=5,
    ))

# get pool info
try:
    variables = {"pool_id": POOL_ID}
    response = client.execute(gql(pool_query), variable_values=variables)

    if len(response['liquidityPool']) == 0:
        print("pool not found")
        exit(-1)

    pool = response['liquidityPool']
    current_tick = int(pool["tick"])

    # get tick spacing
    fees = "0.3"
    for fee_pair in pool["fees"]:
        if fee_pair["feeType"] == "FIXED_TRADING_FEE":
            fees = fee_pair["feePercentage"]
            break
    tick_spacing = fee_tier_to_tick_spacing(fees)

    total_liquidity = int(pool["totalLiquidity"])
    total_value_locked_usd = float(pool["totalValueLockedUSD"])
except Exception as ex:
    print("got exception while querying pool data:", ex)
    exit(-1)


# get tick info
tick_mapping = {}
num_skip = 0
try:
    while True:
        print("Querying ticks, num_skip={}".format(num_skip))
        variables = {"num_skip": num_skip, "pool_id": POOL_ID}
        response = client.execute(gql(tick_query), variable_values=variables)

        if len(response["ticks"]) == 0:
            break
        num_skip += len(response["ticks"])
        for item in response["ticks"]:
            tick_mapping[int(item["index"])] = int(item["liquidityNet"])
except Exception as ex:
    print("got exception while querying tick data:", ex)
    exit(-1)

# Start from zero; if we were iterating from the current tick, would start from the pool's total liquidity
liquidity = 0

# Find the boundaries of the price range
# min_tick = min(tick_mapping.keys())
# max_tick = max(tick_mapping.keys())

# Compute the tick range. This code would work as well in Python: `current_tick // tick_spacing * tick_spacing`
# However, using floor() is more portable.
current_range_bottom_tick = math.floor(current_tick / tick_spacing) * tick_spacing

current_price = tick_to_price(current_tick)
# ETH and USD decimals diff is 12
adjusted_current_price = adjust_price(current_price)

# Sum up all tokens in the pool
total_amount0 = 0
total_amount1 = 0

# Iterate over the tick map starting from the bottom
# token0: ETH, token1: USDC
decimals0 = 18
decimals1 = 6

sorted_tick_list = sorted(tick_mapping.keys())
for tick in sorted_tick_list:
    liquidity_delta = tick_mapping.get(tick, 0)
    liquidity += liquidity_delta

    price = tick_to_price(tick)
    adjusted_price = adjust_price(price)

    should_print_tick = liquidity != 0
    if should_print_tick:
        print("ticks=[{}, {}], bottom tick price={:.2f} USD/ETH".format(tick, tick + tick_spacing, adjusted_price))

    # Compute square roots of prices corresponding to the bottom and top ticks
    bottom_tick = tick
    top_tick = bottom_tick + tick_spacing
    sa = tick_to_price(bottom_tick // 2)
    sb = tick_to_price(top_tick // 2)

    if tick < current_range_bottom_tick:
        # Compute the amounts of tokens potentially in the range
        amount1 = liquidity * (sb - sa)
        amount0 = amount1 / (sb * sa)

        # Only token1 locked
        total_amount1 += amount1

        if should_print_tick:
            adjusted_amount0 = amount0 / (10 ** decimals0)
            adjusted_amount1 = amount1 / (10 ** decimals1)
            print("        {:.2f} USDC locked, potentially worth {:.2f} ETH".format(adjusted_amount1, adjusted_amount0))

    elif tick == current_range_bottom_tick:
        # Always print the current tick. It normally has both assets locked
        print("        Current tick, both assets present!")
        # print("        Current price={:.6f} {}".format(
        #     1 / adjusted_current_price if invert_price else adjusted_current_price, tokens))

        # Print the real amounts of the two assets needed to be swapped to move out of the current tick range
        current_sqrt_price = tick_to_price(current_tick / 2)
        # amount0actual = liquidity_delta * (sb - current_sqrt_price) / (current_sqrt_price * sb)
        # amount1actual = liquidity_delta * (current_sqrt_price - sa)
        amount0actual = liquidity * (sb - current_sqrt_price) / (current_sqrt_price * sb)
        amount1actual = liquidity * (current_sqrt_price - sa)
        adjusted_amount0actual = amount0actual / (10 ** decimals0)
        adjusted_amount1actual = amount1actual / (10 ** decimals1)

        total_amount0 += amount0actual
        total_amount1 += amount1actual

        print("        {:.2f} ETH and {:.2f} USDC remaining in the current tick range".format(
            adjusted_amount0actual, adjusted_amount1actual))


    else:
        # Compute the amounts of tokens potentially in the range
        # amount1 = liquidity_delta * (sb - sa)
        amount1 = liquidity * (sb - sa)
        amount0 = amount1 / (sb * sa)

        # Only token0 locked
        total_amount0 += amount0

        if should_print_tick:
            adjusted_amount0 = amount0 / (10 ** decimals0)
            adjusted_amount1 = amount1 / (10 ** decimals1)
            print("        {:.2f} ETH locked, potentially worth {:.2f} USDC".format(adjusted_amount0, adjusted_amount1))


print("In total: {:.2f} ETH and {:.2f} USDC".format(
    total_amount0 / 10 ** decimals0, total_amount1 / 10 ** decimals1))
# print("Total liquidity: {}".format(liquidity))
