import logging
import os
from datetime import datetime

import pandas as pd
from src.caching.iex_data_cacher import HistoricalDataCacher

os.environ["IEX_API_VERSION"] = "iexcloud-sandbox"
IEX_TOKEN = "Tpk_57fa15c2c86b4dadbb31e0c1ad1db895"


def test_iex_data_cache(capsys):
    store_filename = "test_iex_store.h5"
    symbols = ["A", "AA", "AAA"]
    num_years = 1
    start_date = datetime.strptime("2020-08-25", "%Y-%m-%d")
    end_date = datetime.strptime("2020-12-12", "%Y-%m-%d")

    os.remove(store_filename)
    store = pd.HDFStore(store_filename)

    assert len(store) == 0
    assert store.keys() == []

    captured = capsys.readoutstd()

    data_cacher = HistoricalDataCacher(
        IEX_TOKEN, symbols, store, num_years, start_date, end_date
    )
    data_cacher.cache_data()
    store = pd.HDFStore(store_filename)

    print("OLSH", captured.out)
    print("OLSH", captured.err)

    assert len(store) == 3
    assert store.keys() == ["/A", "/AA", "/AAA"]

    aa_df = store["AA"]
    assert list(aa_df.columns) == ["close", "volume"]
    assert min(aa_df.index) == pd.Timestamp("2020-08-25 00:00:00")
    assert max(aa_df.index) == pd.Timestamp("2020-12-11 00:00:00")
