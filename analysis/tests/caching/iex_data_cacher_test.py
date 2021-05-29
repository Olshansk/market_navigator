import pytest
import logging
import pandas as pd

from datetime import datetime
from src.caching.iex_data_cacher import HistoricalDataCacher

IEX_TOKEN = "Tpk_57fa15c2c86b4dadbb31e0c1ad1db895"

def test_iex_data_cache():
    symbols = ['A', 'AA', 'AAA']
    store = pd.HDFStore("dev_iex_store.h5")
    logging.info("Done loading store into memory.", flush=True)

    data_cacher = HistoricalDataCacher(IEX_TOKEN, symbols, store, NUM_YEARS_HISTORY, START_DATE, END_DATE)
    # data_cacher = HistoricalDataCacher(IEX_TOKEN, symbols, store, 1)
    # data_cacher.cache_data()
    # logging.info("Done caching data.", flush=True)