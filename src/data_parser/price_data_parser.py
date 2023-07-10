import pandas as pd

from utils import utils


def parse_yahoo_data(file_path, start_datetime="0000-00-00"):
    df = pd.read_csv(file_path)
    records = df.to_dict("records")
    data = []
    for item in records:
        if item["Date"] >= start_datetime:
            item_dict = dict()
            item_dict["datetime"] = item["Date"]
            item_dict["price"] = float(item["Open"])
            data.append(item_dict)
    return data


def parse_polygon_data(file_path, start_datetime, end_datetime=None):
    df = pd.read_csv(file_path)
    records = df.to_dict("records")
    data = []
    for item in records:
        datetime = utils.utc_timestamp_to_datetime_ms_str(item["t"])
        if (end_datetime is None and start_datetime <= datetime) or (
                end_datetime is not None and start_datetime <= datetime <= end_datetime):
            item_dict = dict()
            item_dict["datetime"] = datetime
            item_dict["price"] = float(item["o"])
            data.append(item_dict)
    return data
