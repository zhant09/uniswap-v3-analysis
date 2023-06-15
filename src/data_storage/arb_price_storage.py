import gzip
import logging
import logging.handlers
import os
import time

from web3 import Web3

from utils.config import conf, BASE_PATH
from utils import math_utils
from utils import arb_abi


# ARB 0.05% USDC/ETH pool
POOL_ADDRESS = "0xC31E54c7a869B9FcBEcc14363CF510d1c41fa443"  

class GZipRotator:
    def __call__(self, source, dest):
        os.rename(source, dest)
        f_in = open(dest, 'rb')
        f_out = gzip.open("%s.gz" % dest, 'wb')
        f_out.writelines(f_in)
        f_out.close()
        f_in.close()
        os.remove(dest)


log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
log = logging.handlers.TimedRotatingFileHandler(BASE_PATH + '/logs/' + 'arb_price_storage.log', 'midnight', 1, backupCount=30)
log.setLevel(logging.INFO)
log.setFormatter(log_formatter)
log.rotator = GZipRotator()

logger = logging.getLogger(__name__)
logger.addHandler(log)
logger.setLevel(logging.INFO)


def main():
    arbitrum_url = conf.get_config('INFURA', 'arb_url')
    logger.info('Starting Arb Price Storage')
    web3 = Web3(Web3.HTTPProvider(arbitrum_url))
    pool_contract = web3.eth.contract(address=POOL_ADDRESS, abi=arb_abi.arb_pool_abi)
    slot0_func = pool_contract.functions.slot0()

    while True:
        start_time = int(time.time() * 1000)
        slot0 = slot0_func.call()
        end_time = int(time.time() * 1000)
        sqrt_price = slot0[0]
        tick = slot0[1]
        logger.info("start_time: %s, tick: %s, tick_price: %s, sqrt_price: %s, time_cost: %s", start_time, tick, 
                    math_utils.tick_to_price(tick), math_utils.sqrt_price_normalize(sqrt_price), end_time - start_time)
        

if __name__ == "__main__":
    main()
