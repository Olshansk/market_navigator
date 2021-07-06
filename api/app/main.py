import datetime
import json
import logging
import os
# TODO: Remove this
import sys

sys.path.append("..")
from time import gmtime
from typing import Optional

from fastapi import FastAPI

from app.data.processor import compute_new_data
from app.data.reader import read_daily_data_from_hdf
from app.files.keys import get_json_key
from app.files.s3 import download_file, file_last_modified_timestamp, BUCKET_PRIVATE


# DAILY_DATA_HDF5_PATH = os.getenv("DAILY_DATA_HDF5_PATH", "/Volumes/SDCard/Quandl/daily_data.h5")
DAILY_DATA_HDF5_PATH = os.getenv("DAILY_DATA_HDF5_PATH", '/tmp/daily_data.h5')

def _updated_today(date: Optional[datetime.datetime]) -> bool:
    return date and gmtime().tm_mday == date.day

def _maybe_download_data_files():
    if not os.path.isfile(DAILY_DATA_HDF5_PATH):
        download_file('daily_data.h5', DAILY_DATA_HDF5_PATH, BUCKET_PRIVATE)

_maybe_download_data_files()
app = FastAPI()

@app.get("/charts/mayer_multiple/{ticker}/png")
def get_data_for_ticker(ticker: str):
    logging.debug(f"Retrieving data for {ticker}.")
    key = get_json_key(ticker)
    date = file_last_modified_timestamp(key)
    local_file = f"/tmp/{ticker}.cache"
    df = read_daily_data_from_hdf(DAILY_DATA_HDF5_PATH, ticker)
    if not _updated_today(date) and not compute_new_data(ticker, df):
        try:
            os.remove(local_file)
        except OSError:
            pass
        return {"message": f"Data for {ticker} does not exists", "img": ""}

    if os.path.isfile(local_file):
        logging.debug(f"Cache file {local_file} found.")
    else:
        download_file(key, local_file)

    with open(local_file, "r") as f:
        data = json.load(f)
        return {"message": data["message"], "img": data["png"]}
