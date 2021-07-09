from datetime import datetime

import os
import pandas as pd
import fire

import logging
logging.basicConfig(level=logging.DEBUG)
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

def _format_df_for_h5(df: pd.DataFrame):
    df.set_index("date")
    df.index = pd.to_datetime(df["date"])
    df = df.drop(columns=['date'])
    df.sort_index(inplace=True)
    return df

def recompute_daily_data_from_csv(
    output_dir: str,
    sharadar_daily_path: str,
    sharadar_sep_path: str
) -> None:
    logger.debug("About to load data from csv")
    daily_metrics = pd.read_csv(sharadar_daily_path)
    daily_prices = pd.read_csv(sharadar_sep_path)

    logger.debug("About to compute data from csv")
    df_temp = daily_prices[['ticker', 'date','closeadj']].copy().rename(columns={'closeadj': 'price'})
    daily_data = daily_metrics.merge(df_temp, on=['date', 'ticker'], how='inner')
    daily_data['lastupdated'] = pd.to_datetime(daily_data['lastupdated'])
    daily_data.sort_values(by=['date'], inplace=True)
    daily_data = daily_data.reset_index()
    daily_data.drop(columns=['index'], inplace=True)

    logger.debug("About to write full daily data to feather")
    daily_data.to_feather(os.path.join(output_dir, 'daily_data.feather'))

    logger.debug("About to write full daily data to hdf5")
    daily_data = _format_df_for_h5(daily_data)
    try:
        write_daily_data_to_hdf(daily_data, output_dir)
    except:
        print(f"""
        **************************************************************************
        There was an error write the feather data to HDFStore.
        Try doing the following:
            ipython
            import pandas as pd

            df = pd.from_feather('{os.path.join(output_dir, 'daily_data.feather')}')
            df.set_index("date")
            df.index = pd.to_datetime(daily_data["date"])
            df = daily_data.drop(columns=['date'])
            df.sort_index(inplace=True)
            df.to_hdf({os.path.join(output_dir, 'daily_data.h5')}, key='daily_data', format='t', data_columns=['ticker'])

            https://github.com/pandas-dev/pandas/issues/2773#issuecomment-56779269
        **************************************************************************
        """)

    logger.debug(f'Wrote new data to {output_dir}')

def write_daily_data_to_hdf(df: pd.DataFrame, output_dir: str):
    filename = os.path.join(output_dir, 'daily_data.h5')
    df.to_hdf(
        filename,
        key='daily_data',
        format='t',
        data_columns=['ticker'])
    store = pd.HDFStore(filename)
    store.get_storer('daily_data').attrs.last_date = df.index[-1].strftime('%Y-%m-%d')
    store.get_storer('daily_data').attrs.tickers = ';'.join(list(df['ticker'].unique()))
    store.close()

def append_to_daily_data_hdf(hdf_path: str) -> pd.DataFrame:
    store = pd.HDFStore(hdf_path)
    last_date = store.get_storer('daily_data').attrs.last_date

    logging.info("About to load new data after {last_append}")
    new_daily_data = quandl.get_table('SHARADAR/DAILY', date={'gte': last_date}, paginate=True)
    new_sep_data = quandl.get_table('SHARADAR/SEP', date={'gte': last_date}, paginate=True)

    logging.info("About to process new data")
    new_data = _merge_sep_and_daily_dfs(new_daily_data, new_sep_data)
    new_data = _format_df_for_h5(new_data)

    store.append('daily_data', new_data)
    store.get_storer('daily_data').attrs.last_date = new_data.index[-1].strftime('%Y-%m-%d')
    all_tickers = set(store.get_storer('daily_data').attrs.tickers.split(';')).union(set(new_data['ticker'].unique()))
    store.get_storer('daily_data').attrs.tickers = all_tickers
    store.close()

if __name__ == '__main__':
  fire.Fire({
      'recompute': recompute_daily_data_from_csv,
      'append': append_to_daily_data_hdf
  })