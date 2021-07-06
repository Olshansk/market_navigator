from datetime import datetime

import os
import pandas as pd
import fire

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.debug(' Debug is working')

import quandl
quandl.ApiConfig.api_key = os.getenv('QUANDL_API_KEY')

DEV_FEATHER_PATH = "/Volumes/SDCard/Quandl/daily_data.feather"

# https://www.quandl.com/tables/SFA/SHARADAR-SEP/export
# https://www.quandl.com/tables/SFA/SHARADAR-DAILY/export
def download_quandl_tables(output_dir: str) -> None:
    """WARNING: Extremeley slow operation."""
    d = datetime.now().strftime('%Y_%m_%d')
    dir_base = os.path.join(output_dir, 'Quandl', d)
    os.mkdir(dir_base)

    logger.debug(f"Downloading shardar daily tables to {dir_base}")
    quandl.export_table('SHARADAR/DAILY', filename=os.path.join(dir_base, 'SHARADAR-DAILY.zip'))

    logger.debug(f"Downloading sep daily to tables to {dir_base}")
    quandl.export_table('SHARADAR/SEP', filename=os.path.join(dir_base, 'SHARADAR-SEP.zip'))

def read_daily_data_from_feather(daily_data_path: str = DEV_FEATHER_PATH) -> pd.DataFrame:
    """ Read in the full daily data DF into memory.

    We're not storing the datetime index because feather does not support it.
    """
    df = pd.read_feather(daily_data_path)
    df['lastupdated'] = pd.to_datetime(df['lastupdated'])
    df.set_index("date")
    df.index = pd.to_datetime(df["date"])
    df.drop(columns=['date'], inplace=True)
    df.sort_index(inplace=True)
    assert df.index.duplicated().sum() == 0, "Duplicate dates in daily data"
    return df

def read_daily_data_from_hdf(hdf_path: str, ticker: str):
    store = pd.HDFStore(hdf_path)
    return store.select('daily_data', where=f'ticker={ticker}')

if __name__ == '__main__':
  fire.Fire({
      'download': download_quandl_tables
  })