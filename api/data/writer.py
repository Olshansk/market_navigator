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

DEV_HDF5_PATH = "/Volumes/SDCard/Quandl/daily_data.h5"

def _merge_sep_and_daily_dfs(
    df_daily: pd.DataFrame,
    df_sep: pd.DataFrame
) -> pd.DataFrame:
    df_temp = df_sep[['ticker', 'date','closeadj']].copy().rename(columns={'closeadj': 'price'})
    return df_daily.merge(df_temp, on=['date', 'ticker'], how='inner').sort_values(by=['date'], inplace=False)

def recompute_daily_data_from_csv(
    output_dir: str,
    sharadar_daily_path: str,
    sharadar_sep_path: str
) -> pd.DataFrame:
    logger.debug("About to load data from csv")
    daily_metrics = pd.read_csv(sharadar_daily_path)
    daily_prices = pd.read_csv(sharadar_sep_path)

    logger.debug("About to compute data from csv")
    df_temp = daily_prices[['ticker', 'date','closeadj']].copy().rename(columns={'closeadj': 'price'})
    daily_data = daily_metrics.merge(df_temp, on=['date', 'ticker'], how='inner')
    daily_data.sort_values(by=['date'], inplace=True)

    logger.debug("About to write full daily data to feather")
    daily_data.reset_index().to_feather(os.path.join(output_dir, 'daily_data.feather'))
    logger.debug("About to write full daily data to hdf5")
    write_daily_data_to_hdf(daily_data, output_dir)

    logger.debug(f'Wrote new data to {output_dir}')
    return daily_data

def write_daily_data_to_hdf(df: pd.DataFrame, output_dir: str):
    filename = os.path.join(output_dir, 'daily_data.h5')
    df.to_hdf(
        filename,
        key='daily_data',
        format='t',
        data_columns=['ticker'])
    store = pd.HDFStore(filename)
    store.get_storer('daily_data').attrs.last_date = df.index[-1].strftime('%Y-%m-%d')
    store.close()

def append_to_daily_data_hdf(hdf_path: str) -> pd.DataFrame:
    store = pd.HDFStore(hdf_path)
    last_date = store.get_storer('daily_data').attrs.last_date

    logging.debug("About to load new data")
    new_daily_data = quandl.get_table('SHARADAR/DAILY', date={'gte': last_date}, paginate=True)
    new_sep_data = quandl.get_table('SHARADAR/SEP', date={'gte': last_date}, paginate=True)

    logging.debug("About to process new data")
    new_data = _merge_sep_and_daily_dfs(new_daily_data, new_sep_data)
    new_data.set_index("date")
    new_data.index = pd.to_datetime(new_data["date"])
    new_data = new_data.drop(columns=['date'])
    new_data.sort_index(inplace=True)

    store.append('daily_data', new_data)
    store.get_storer('daily_data').attrs.last_date = new_data.index[-1].strftime('%Y-%m-%d')
    store.close()

if __name__ == '__main__':
  fire.Fire({
      'recompute': recompute_daily_data_from_csv,
      'append': append_to_daily_data_hdf
  })