import asyncio
import logging
import datetime
import time

from kucoin.client import Client
from kucoin.asyncio import KucoinSocketManager

from utils.config import BASE_PATH


log_file = BASE_PATH + "/logs/" + datetime.datetime.now().strftime('eth_socket_order_%Y%m%d.log')
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(module)s %(levelname)s %(message)s')


api_key = '<api_key>'
api_secret = '<api_secret>'
api_passphrase = '<api_passphrase>'


async def main():
    global loop

    # callback function that receives messages from the socket
    async def handle_evt(msg):
        # if msg['topic'] == '/spotMarket/level2Depth5:ETH-USDC':
        logging.info(msg["data"])
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
    logging.info("Start fetching eth socket order data")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
