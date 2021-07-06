import datetime
import logging
import time
from typing import Any, List, Optional

import pandas as pd
from dateutil.relativedelta import relativedelta
from iexfinance.stocks import get_historical_data


# Assumptions:
# 1. No missing data in existing dataframes in the store; data is complete between (date_min, date_max).
# 2. The requested data is of the same format (URL, params, retrieved columns, etc...).
# Reference for metadata: https://moonbooks.org/Articles/How-to-add-metadata-to-a-data-frame-with-pandas-in-python-/#store-in-a-hdf5-file
def _update_store_data(
    store: pd.HDFStore,
    symbol: str,
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    **kwargs: Optional[Any],
):

    # This is necessary to avoid fetching new data if the hours/minutes/seconds changed.
    def _sanitize_date(date):
        return datetime.datetime(date.year, date.month, date.day)

    # This is necessary for performance reasons to avoid inferring column
    # types when saving the files.
    def _format_df_columns(df):
        df["close"] = pd.to_numeric(df["close"])
        df["volume"] = pd.to_numeric(df["volume"])
        return df

    start_date = _sanitize_date(start_date)
    end_date = _sanitize_date(end_date)

    print(
        f"{symbol}: Trying to access historical data between {start_date} and {end_date}."
    )

    if symbol not in store:
        logging.debug(f"{symbol}: No data is cached.")
        df = _format_df_columns(
            get_historical_data(symbol, start_date, end_date, **kwargs)
        )
        metadata = {"min_date": start_date, "max_date": end_date}
    else:
        df = store[symbol]
        metadata = store.get_storer(symbol).attrs.metadata

        logging.debug(
            f"{symbol}: Data is catched between {metadata['min_date']} and {metadata['max_date']}."
        )

        if start_date < metadata["min_date"]:
            logging.debug(
                f"{symbol}: Requesting data between {start_date} and {metadata['min_date']}."
            )
            df = df.append(
                _format_df_columns(
                    get_historical_data(
                        symbol, start_date, metadata["min_date"], **kwargs
                    )
                )
            )
            metadata["min_date"] = start_date

        if end_date > metadata["max_date"]:
            logging.debug(
                f"{symbol}: Requesting data between {metadata['max_date']} and {end_date}."
            )
            df = df.append(
                _format_df_columns(
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


class HistoricalDataCacher:
    def __init__(
        self,
        iex_token: str,
        symbols: List[str],
        store: pd.HDFStore,
        num_historical_years: int = 1,
        start_date: datetime.datetime = None,
        end_date: datetime.datetime = None,
    ) -> None:
        self.iex_token = iex_token
        self.symbols = symbols
        self.store = store
        self.num_historical_years = num_historical_years
        self.start_date = start_date
        self.end_date = end_date
        pass

    RATE_LIMIT_REQUESTS = 1000000
    RATE_LIMIT_SLEEP = 10

    def _get_dates(self):
        if None not in (self.start_date, self.end_date):
            return (self.start_date, self.end_date)

        end_date = datetime.datetime.now()
        start_date = end_date - relativedelta(years=self.num_historical_years)
        # Need to add a delta because 15 years is the max: https://iexcloud.io/docs/api/#historical-prices
        start_date += (
            relativedelta(days=7)
            if self.num_historical_years >= 15
            else relativedelta(days=0)
        )
        return (start_date, end_date)

    def _close_store(self):
        try:
            self.store.close()
            print("Successfully closed `store` file.")
        except Exception:
            logging.exception("Error closing store.")

    def _flush_store(self):
        try:
            print("About to flush the store")
            self.store.flush(fsync=True)
        except Exception:
            logging.exception("Error flushing store.")

    def _cache_data(self):
        num_requests_since_last_sleep = 0
        (start_date, end_date) = self._get_dates()
        for symbol in self.symbols:
            try:
                _update_store_data(
                    self.store,
                    symbol,
                    start_date,
                    end_date,
                    close_only=True,
                    output_format="pandas",
                    token=self.iex_token,
                )
                num_requests_since_last_sleep += 1
                if num_requests_since_last_sleep > self.RATE_LIMIT_REQUESTS:
                    self._flush_store()
                    time.sleep(self.RATE_LIMIT_SLEEP)
                    num_requests_since_last_sleep = 0
            except:
                logging.exception(f"Failed to process {symbol}")

    def cache_data(self):
        self._cache_data()
        self._flush_store()
        self._close_store()
