import datetime
import json
import os
import logging
# TODO: Remove this
import sys
sys.path.append("..")
from time import gmtime
from typing import Optional
from fastapi import FastAPI


from api.files.keys import get_json_key
from api.files.s3 import file_last_modified_timestamp, download_file
from api.data.reader import read_daily_data_df
from api.data.processor import compute_new_data


def _updated_today(date: Optional[datetime.datetime]) -> bool:
    return date and gmtime().tm_mday == date.day


app = FastAPI()
df = read_daily_data_df()  # Warmup


@app.get("/charts/mayer_multiple/png/{ticker}")
def get_data_for_ticker(ticker: str):
    logging.debug(f"Retrieving data for {ticker}.")
    key = get_json_key(ticker)
    date = file_last_modified_timestamp(key)
    local_file = f'/tmp/{ticker}.cache'
    if not _updated_today(date) and not compute_new_data(ticker, df):
        try:
            os.remove(local_file)
        except OSError:
            pass
        return {"message": f"Data for {ticker} does not exists", 'img': ''}
    if os.path.isfile(local_file):
        logging.debug(f"Cache file {local_file} found.")
    else:
        download_file(key, local_file)

    with open(local_file, 'r') as f:
        data = json.load(f)
        return {"message": data["message"], "img": data['png']}
