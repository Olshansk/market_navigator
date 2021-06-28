import datetime
import json
from typing import Optional
from fastapi import FastAPI
from time import gmtime
from fastapi import Depends

import logging
import pandas as pd

import sys
sys.path.append('..')

from analysis.src.mayer_multiple.compute_metrics import compute_mm_metrics_for_ticker, format_message
from analysis.src.mayer_multiple.plot_metrics import build_mm_histogram
from api.files.s3 import upload_file, file_exists

def _read_in_data():
    df_full = pd.read_feather('/Users/olshansky/workspace/tip/daily_data.feather')
    df_full.set_index('date')
    df_full.index = pd.to_datetime(df_full['date'])
    return df_full.sort_index()

def _compute_new_data(ticker, key):
    df = compute_mm_metrics_for_ticker(df_full, ticker)
    if df is None: raise Exception(f'Data for {ticker} does not exist.')
    logging.debug(f'Computing data for {ticker}.')
    (chart, _) = build_mm_histogram(df)

    filename = f'/tmp/{key}'
    data = {
        'message': format_message(df, ticker),
        'chart': chart.to_json()
    }
    with open(filename, 'w') as f:
        json.dump(data, f)
    upload_file(filename, key=key)


app = FastAPI()
df_full = _read_in_data()

@app.get("/charts/mayer_multiple/{ticker}")
def get_data_for_ticker(ticker: str):
    logging.debug(f'Retrieving data for {ticker}.')
    key = f'mm_chart_{ticker}.json'
    date = file_exists(key)
    if not date or gmtime().tm_mday != date.day:
        try:
            _compute_new_data(ticker, key)
        except Exception as e:
            logging.error(e)
            return {
                'message': 'Error',
                'error_message': f'Data for {ticker} does not exists'
            }
    return {
        'message': 'message',
        'chart': key
    }
