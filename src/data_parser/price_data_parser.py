import pandas as pd

from utils import utils


def parse_daily_data(file_path, date_column="Date", price_column="Open", start_datetime="0000-00-00",
                     end_datetime=None, price_inverse=False, unix_timestamp_ms=False):
    df = pd.read_csv(file_path)
    records = df.to_dict("records")
    data = []
    for item in records:
        datetime = item[date_column]
        if unix_timestamp_ms:
            datetime = utils.utc_timestamp_to_datetime_ms_str(datetime)[:10]
        if (end_datetime is None and start_datetime <= datetime) or (
                end_datetime is not None and start_datetime <= datetime <= end_datetime):
            item_dict = dict()
            item_dict["datetime"] = datetime
            item_dict["price"] = float(item[price_column])
            if price_inverse:
                item_dict["price"] = 1 / item_dict["price"]
            data.append(item_dict)
    return data


def parse_hourly_data(file_path, date_column="t", price_column="o", start_datetime="0000-00-00 00:00:00",
                      end_datetime=None, price_inverse=False, unix_timestamp_ms=True):
    df = pd.read_csv(file_path)
    records = df.to_dict("records")
    data = []
    for item in records:
        datetime = item[date_column]
        if unix_timestamp_ms:
            datetime = utils.utc_timestamp_to_datetime_ms_str(datetime)[:-4]
        if (end_datetime is None and start_datetime <= datetime) or (
                end_datetime is not None and start_datetime <= datetime <= end_datetime):
            item_dict = dict()
            item_dict["datetime"] = datetime
            item_dict["price"] = float(item[price_column])
            if price_inverse:
                item_dict["price"] = 1 / item_dict["price"]
            data.append(item_dict)
    return data
