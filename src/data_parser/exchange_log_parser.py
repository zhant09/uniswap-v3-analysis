import json

from tqdm import tqdm


def parse_cex_data(file_path):
    result = []
    with open(file_path) as rf:
        line = rf.readline()
        while line:
            if "{" in line:
                data = line.split("INFO")[1].strip()
                result.append(json.loads(data.replace("'", '"')))
            line = rf.readline()
    return result


def parse_dex_data(file_path):
    result = []
    with open(file_path) as rf:
        line = rf.readline()
        while line:
            line_dict = dict()
            if "start_time" in line:
                data = line.split("INFO")[1].strip()
                line_dict["start_time"] = data.split("start_time: ")[1].split(",")[0]
                line_dict["tick"] = int(data.split("tick: ")[1].split(",")[0])
                line_dict["tick_price"] = float(data.split("tick_price: ")[1].split(",")[0])
                line_dict["sqrt_price"] = float(data.split("sqrt_price: ")[1].split(",")[0])
                line_dict["time_cost"] = int(data.split("time_cost: ")[1].split(",")[0])
                result.append(line_dict)
            line = rf.readline()
    return result


def _get_cex_price(cex_data, dex_time_key):
    price_dict = dict()
    for item in cex_data:
        if item["timestamp"] > dex_time_key:
            ask_price = float(item["asks"][0][0])
            bid_price = float(item["bids"][0][0])
            price_dict["cex_time"] = item["timestamp"]
            price_dict["cex_price"] = (ask_price + bid_price) / 2
            # price_dict["cex_bid_price"] = bid_price
            return price_dict


# since dex data is sparse, we use dex data as base
def combine_dex_cex(dex_data, cex_data):
    result = []
    for i in tqdm(range(len(dex_data) - 1)):
        item = dex_data[i]
        dex_time_key = int(item["start_time"]) + item["time_cost"]
        price_dict = _get_cex_price(cex_data, dex_time_key)
        price_dict["dex_time"] = dex_time_key
        price_dict["dex_tick_price"] = item["tick_price"]
        price_dict["dex_price"] = item["sqrt_price"]

        result.append(price_dict)
    return result
