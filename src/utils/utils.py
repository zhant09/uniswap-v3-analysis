from datetime import datetime, timezone


def date_to_utc_timestamp(c_date):
    return int(c_date.replace(tzinfo=timezone.utc).timestamp())


def utc_timestamp_to_date(ts):
    return datetime.fromtimestamp(ts, tz=timezone.utc)


def utc_timestamp_to_date_str(ts):
    utc_date = datetime.fromtimestamp(ts, tz=timezone.utc)
    return utc_date.strftime("%Y-%m-%d")


# print(date_to_utc_timestamp(datetime(2023, 5, 1)))
# print(utc_timestamp_to_date_str(1620086400))

