import json

from tqdm import tqdm
from utils import utils


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


def _cex_to_dict(cex_data):
    cex_dict = dict()
    for item in cex_data:
        unix_time_sec = int(item["timestamp"]/1000)
        if unix_time_sec in cex_dict:
            cex_dict[unix_time_sec].append(item)
        else:
            cex_dict[unix_time_sec] = [item]
    return cex_dict


# time_range: valid cex data time range compare to dex time_key, 1 second means cex data could be 1 sec diff from dex
def _get_cex_price(dex_time_key, cex_dict, time_range):
    price_dict = dict()
    time_key_sec = int(dex_time_key/1000)
    for r in range(time_range+1):
        time_key_sec += r
        if time_key_sec not in cex_dict:
            continue

        cex_sec_list = cex_dict[time_key_sec]
        for item in cex_sec_list:
            if item["timestamp"] > dex_time_key:
                ask_price = float(item["asks"][0][0])
                bid_price = float(item["bids"][0][0])
                price_dict["cex_time"] = item["timestamp"]
                price_dict["cex_price"] = (ask_price + bid_price) / 2
                return price_dict
    return None


# since dex data is sparse, we use dex data as base
def combine_dex_cex(dex_data, cex_data, time_range):
    cex_dict = _cex_to_dict(cex_data)

    result = []
    for i in tqdm(range(len(dex_data) - 1)):
        item = dex_data[i]
        dex_time_key = int(item["start_time"]) + item["time_cost"]
        price_dict = _get_cex_price(dex_time_key, cex_dict, time_range)
        if price_dict is None:
            # for debug
            # print("dex_time_key: {} not found in cex data".format(
            #     utils.utc_timestamp_to_datetime_ms_str(dex_time_key)))
            continue
        price_dict["dex_time"] = dex_time_key
        price_dict["dex_tick_price"] = item["tick_price"]
        price_dict["dex_price"] = item["sqrt_price"]
        result.append(price_dict)
    return result


# if __name__ == '__main__':
#     cex_data = parse_cex_data("../../logs/eth_socket_order.log.2023-06-15")
#     dex_data = parse_dex_data("../../logs/arb_price_storage.log.2023-06-15")
#     combine_result = combine_dex_cex(dex_data, cex_data)
#     print(len(combine_result))
