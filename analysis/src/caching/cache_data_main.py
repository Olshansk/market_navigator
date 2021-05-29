import argparse
import tables
import logging
import os
import time
import warnings
import requests_cache
import pandas as pd

from iexfinance.refdata import get_symbols
from datetime import datetime
from analysis.src.caching import HistoricalDataCacher


if os.getenv("ENVIRONMENT") == "PROD":
    os.environ["IEX_API_VERSION"] = "iexcloud-v1"
    RATE_LIMIT_REQUESTS = 100
    RATE_LIMIT_SLEEP = 10
    IEX_TOKEN = os.getenv("IEX_TOKEN", "pk_5839e587dee649c7a3653e6fbadf7230")
    FIRST_SYMBOL_IDX = int(os.getenv("FIRST_SYMBOL_IDX"), "0")
    LAST_SYMBOL_IDX = int(os.getenv("LAST_SYMBOL_IDX"), "-1")
    NUM_YEARS_HISTORY = int(os.getenv("NUM_YEARS_HISTORY"), "14")
    START_DATE = None
    END_DATE = None
else:
    requests_cache.install_cache("iex_cache")
    os.environ["IEX_API_VERSION"] = "iexcloud-sandbox"
    IEX_TOKEN = "Tpk_57fa15c2c86b4dadbb31e0c1ad1db895"
    FIRST_SYMBOL_IDX = 0
    LAST_SYMBOL_IDX = 11
    NUM_YEARS_HISTORY = 4
    RATE_LIMIT_REQUESTS = 1000000
    RATE_LIMIT_SLEEP = 10
    START_DATE = datetime.strptime("2020-08-25", '%Y-%m-%d')
    END_DATE = datetime.strptime("2020-12-12", '%Y-%m-%d')


def main():
    all_symbols = get_symbols(token=IEX_TOKEN)
    symbols = all_symbols[FIRST_SYMBOL_IDX:LAST_SYMBOL_IDX]
    symbols = [symbol_metadata["symbol"] for _, symbol_metadata in symbols.iterrows()]
    logging.info(
        f"Retrieved {len(all_symbols)} symbols. About to process {FIRST_SYMBOL_IDX} to {LAST_SYMBOL_IDX}",
        flush=True,
    )

    store = pd.HDFStore("dev_iex_store.h5")
    logging.info("Done loading store into memory.", flush=True)

    data_cacher = HistoricalDataCacher(symbols, store)
    data_cacher.cache_data()
    logging.info("Done caching data.", flush=True)


if __name__ == "__main__":
    with warnings.catch_warnings():
        # This happens when we try to save a symbol such as 'AAIC-B' in the HDF5 store
        # More details here: https://stackoverflow.com/questions/58414068/how-to-get-rid-of-naturalnamewarning
        warnings.filterwarnings("ignore", category=tables.NaturalNameWarning)
        main()
