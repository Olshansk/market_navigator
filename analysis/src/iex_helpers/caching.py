from datetime import date, datetime

import pandas as pd
from iexfinance.stocks import get_historical_data


# Assumptions:
# 1. No missing data in existing dataframes in the store; data is complete between (date_min, date_max).
# 2. The requested data is of the same format (URL, params, retrieved columns, etc...).
# Reference for metadata: https://moonbooks.org/Articles/How-to-add-metadata-to-a-data-frame-with-pandas-in-python-/#store-in-a-hdf5-file
def get_historical_data_cached(store, symbol, start_date, end_date, **kwargs):
    # This is necessary to avoid fetching new data if the hours/minutes/seconds changed.
    def sanitize_date(date):
        return datetime(date.year, date.month, date.day)

    # This is necessary for performance reasons to avoid inferring column
    # types when saving the files.
    def format_df_columns(df):
        df["close"] = pd.to_numeric(df["close"])
        df["volume"] = pd.to_numeric(df["volume"])
        return df

    start_date = sanitize_date(start_date)
    end_date = sanitize_date(end_date)

    print(
        f"{symbol}: Trying to access historical data between {start_date} and {end_date}."
    )

    if symbol not in store:
        print(f"{symbol}: No data is cached.")
        df = format_df_columns(
            get_historical_data(symbol, start_date, end_date, **kwargs)
        )
        metadata = {"min_date": start_date, "max_date": end_date}
    else:
        df = store[symbol]
        metadata = store.get_storer(symbol).attrs.metadata

        print(
            f"{symbol}: Data is catched between {metadata['min_date']} and {metadata['max_date']}."
        )

        if start_date < metadata["min_date"]:
            print(
                f"{symbol}: Requesting data between {start_date} and {metadata['min_date']}."
            )
            df = df.append(
                format_df_columns(
                    get_historical_data(
                        symbol, start_date, metadata["min_date"], **kwargs
                    )
                )
            )
            metadata["min_date"] = start_date

        if end_date > metadata["max_date"]:
            print(
                f"{symbol}: Requesting data between {metadata['max_date']} and {end_date}."
            )
            print(f"delta_days = {(datetime.now() - metadata['max_date']).days}")
            df = df.append(
                format_df_columns(
                    get_historical_data(
                        symbol, metadata["max_date"], end_date, **kwargs
                    )
                )
            )
            metadata["max_date"] = end_date

        # Not using store.append() because of this deduplication need.
        df = df[~df.index.duplicated(keep="first")]

    store[symbol] = df
    store.get_storer(symbol).attrs.metadata = metadata

    return df
