import datetime
import json
import logging
import pathlib
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
from app.files.helpers import rm_f
from app.files.s3 import download_file, file_last_modified_timestamp, BUCKET_PRIVATE


DAILY_DATA_HDF5_PATH = os.getenv("DAILY_DATA_HDF5_PATH", "/Volumes/SDCard/Quandl/daily_data.h5")

def _updated_today(date: Optional[datetime.datetime]) -> bool:
    return date and gmtime().tm_mday == date.day

def _maybe_download_data_files():
    logging.info("Checking if HDFS file is available locally.")
    if not os.path.isfile(DAILY_DATA_HDF5_PATH):
        print("About to start downloading object...")
        download_file('daily_data.h5', DAILY_DATA_HDF5_PATH, BUCKET_PRIVATE)

# _maybe_download_data_files()
app = FastAPI()

@app.get("/items/", )
@app.get("/charts/mayer_multiple/{ticker}/png", include_in_schema=False)
def get_data_for_ticker(ticker: str):
    logging.info(f"Retrieving data for {ticker}.")
    key = get_json_key(ticker)
    date = file_last_modified_timestamp(key)
    local_file = f"/tmp/{ticker}.cache"

    if not _updated_today(date):
        rm_f(local_file)
        df = read_daily_data_from_hdf(DAILY_DATA_HDF5_PATH, ticker)
        if not compute_new_data(ticker, df):
            return {"message": f"Data for {ticker} does not exists", "img": ""}

    if not os.path.isfile(local_file):
        download_file(key, local_file)
        logging.debug(f"Cached file {local_file} not found.")

    with open(local_file, "r") as f:
        data = json.load(f)
        return {"message": data["message"], "img": data["png"]}

@app.get("/charts/mayer_multiple/{ticker}/cached/png")
def get_data_for_ticker(ticker: str):
    logging.info(f"Retrieving cached data for {ticker}.")
    key = get_json_key(ticker)
    last_update_date = file_last_modified_timestamp(key)

    if not last_update_date:
        return {"message": f"Data for {ticker} does not exists.", "img": ""}

    local_file = f"/tmp/{ticker}.cache"
    local_fname = pathlib.Path(local_file)

    if not (local_fname.exists() and datetime.datetime.fromtimestamp(local_fname.stat().st_mtime) > last_update_date):
        rm_f(local_file)
        try:
            download_file(key, local_file)
        except OSError:
            return {"message": f"Error downloading data for {ticker}.", "img": ""}

    with open(local_file, "r") as f:
        data = json.load(f)
        return {"message": data["message"], "img": data["png"]}
