import pandas as pd

import utils


# todo: too simple simulation, provided liquidity distribution is different from all liquidity distribution,
#  need to refine
def data_clean(df):
    df.drop(index=0, inplace=True)
    df["date_str"] = df["date"].apply(utils.utc_timestamp_to_date_str)

    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["btc_eth_low"] = 1 / df["high"]
    df["btc_eth_high"] = 1 / df["low"]
    df["tvlUSD"] = df["tvlUSD"].astype(float)
    df["feesUSD"] = df["feesUSD"].astype(float)
    df["fees_rate"] = df["feesUSD"] / df["tvlUSD"]

    analysis_df = df[["date_str", "feesUSD", "btc_eth_low", "btc_eth_high", "fees_rate"]]
    analysis_df.rename(columns={"date_str": "date", "feesUSD": "fees_usd"}, inplace=True)
    return analysis_df


if __name__ == '__main__':
    csv_file = "../data/wbtc_eth_0.3_uniswap_data.csv"
    pool_df = pd.read_csv(csv_file)
    df = data_clean(pool_df)

