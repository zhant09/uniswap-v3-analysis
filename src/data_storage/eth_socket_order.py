import asyncio
import datetime
import gzip
import logging
import logging.handlers
import os

from kucoin.client import Client
from kucoin.asyncio import KucoinSocketManager

from utils.config import BASE_PATH


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
log = logging.handlers.TimedRotatingFileHandler(BASE_PATH + '/logs/' + 'eth_socket_order.log', 'midnight', 1,
                                                backupCount=30)
log.setLevel(logging.INFO)
log.setFormatter(log_formatter)
log.rotator = GZipRotator()

logger = logging.getLogger(__name__)
logger.addHandler(log)
logger.setLevel(logging.INFO)


api_key = '<api_key>'
api_secret = '<api_secret>'
api_passphrase = '<api_passphrase>'


async def main():
    global loop

    # callback function that receives messages from the socket
    async def handle_evt(msg):
        # if msg['topic'] == '/spotMarket/level2Depth5:ETH-USDC':
        logger.info(msg["data"])
        # file_path = BASE_PATH + "/data/eth_socket_order_{}.json".format(datetime.datetime.now().strftime("%Y%m%d"))
        # async with open(file_path, "w") as wf:
        #     await wf.write(str(msg["data"] + "\n"))
        #     await wf.flush()

    client = Client(api_key, api_secret, api_passphrase)

    ksm = await KucoinSocketManager.create(loop, client, handle_evt)

    # ETH-USDC level2Depth5
    await ksm.subscribe('/spotMarket/level2Depth5:ETH-USDC')

    while True:
        # logging.info("sleeping to keep loop open")
        await asyncio.sleep(30)


if __name__ == "__main__":
    logger.info("Start fetching eth socket order data")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
 