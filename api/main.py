from typing import Optional
from fastapi import FastAPI

import pandas as pd

import sys
sys.path.append('..')

from analysis.src.mayer_multiple.compute_metrics import compute_mm_metrics_for_ticker, format_message
from analysis.src.mayer_multiple.plot_metrics import build_mm_histogram
from api.files.s3 import upload_file

def _read_in_data():
    df_full = pd.read_feather('/Users/olshansky/workspace/tip/daily_data.feather')
    df_full.set_index('date')
    df_full.index = pd.to_datetime(df_full['date'])
    return df_full.sort_index()

app = FastAPI()
df_full = _read_in_data()


@app.get("/charts/mayer_multiple/{ticker}")
def get_data_for_ticker(ticker: str):
    df = compute_mm_metrics_for_ticker(df_full, ticker)
    message = format_message(df, ticker)
    (chart, _) = build_mm_histogram(df)
    filename = f'/tmp/mm_{ticker}.json'
    chart.save(filename)
    print(upload_file(filename))
    return {
        'message': message,
        'chart': chart.to_json()
    }