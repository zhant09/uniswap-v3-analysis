import math

TICK_BASE = 1.0001


def tick_to_price(tick):
    return TICK_BASE ** tick * 1e12


def price_to_tick(price):
    return math.log(price / 1e12, TICK_BASE)


def sqrt_price_normalize(sqrt_price):
    return (sqrt_price / (1 << 96)) ** 2 * 1e12
