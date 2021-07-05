from datetime import datetime
import os
import quandl
import pandas as pd
import fire
quandl.ApiConfig.api_key = os.getenv('QUANDL_API_KEY')

FEATHER_PATH = "/Users/olshansky/workspace/tip/daily_data.feather"

def _merge_sep_and_daily(
    daily: pd.DataFrame,
    sep: pd.DataFrame
) -> pd.DataFrame:
    df_temp = sep[['ticker', 'date','closeadj']].copy().rename(columns={'closeadj': 'price'})
    return daily.merge(df_temp, on=['date', 'ticker'], how='inner').sort_values(by=['date'], inplace=False)

def read_daily_data_df(daily_data_path: str = FEATHER_PATH) -> pd.DataFrame:
    # We're not storing the datetime index because feather does not support it
    df = pd.read_feather(daily_data_path)
    df.set_index("date")
    df.index = pd.to_datetime(df["date"])
    return df.drop(['date']).sort_index()

# https://www.quandl.com/tables/SFA/SHARADAR-SEP/export
# https://www.quandl.com/tables/SFA/SHARADAR-DAILY/export
def download_tables(output_path: str) -> None:
    d = datetime.now().strftime('%Y_%d_%m')
    dir_base = os.path.join(output_path, 'Quandl', d)
    os.mkdir(dir_base)

    print("Downloading shardar daily tables to {}".format(dir_base))
    quandl.export_table('SHARADAR/DAILY', filename=os.path.join(dir_base, 'SHARADAR-DAILY.zip'))

    print("Downloading sep daily to tables to {}".format(dir_base))
    quandl.export_table('SHARADAR/SEP', filename=os.path.join(dir_base, 'SHARADAR-SEP.zip'))

def recompute_df_full_from_csv(
    output_path: str = 'daily_data.feather',
    sharadar_daily_path: str = 'SHARADAR-DAILY.csv',
    sharadar_sep_path: str = 'SHARADAR-SEP.csv'
) -> pd.DataFrame:
    daily_metrics = pd.read_csv(sharadar_daily_path)
    daily_prices = pd.read_csv(sharadar_sep_path)
    df_temp = daily_prices[['ticker', 'date','closeadj']].copy().rename(columns={'closeadj': 'price'})

    daily_data = daily_metrics.merge(df_temp, on=['date', 'ticker'], how='inner')
    daily_data.sort_values(by=['date'], inplace=True)
    df = daily_data.reset_index()
    df.to_feather(output_path)
    return df

def append_to_full_df(daily_data_path: str) -> pd.DataFrame:
    df_full = read_daily_data_df(daily_data_path)
    last_date = df_full.index[-1].strftime('%Y-%m-%d')
    print(f"About to append data after {last_date}")

    print('About to pull new data...')
    new_daily_data = quandl.get_table('SHARADAR/DAILY', date={'gte': last_date}, paginate=True)
    new_sep_data = quandl.get_table('SHARADAR/SEP', date={'gte': last_date}, paginate=True)

    print('About to process new data...')
    new_data = _merge_sep_and_daily(new_daily_data, new_sep_data)
    new_data.set_index("date")
    new_data.index = pd.to_datetime(new_data["date"])
    new_data = new_data.drop(columns=['date'])
    new_data.sort_index(inplace=True)

    print('About to append new data...')
    daily_data = pd.concat([df_full, new_data]).sort_values(by=['date'], inplace=True)
    daily_data.to_feather(daily_data_path)
    return daily_data

if __name__ == '__main__':
  fire.Fire({
      'recompute': recompute_df_full_from_csv,
      'download': download_tables,
      'append': append_to_full_df
  })