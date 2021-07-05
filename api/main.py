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

from data.processor import compute_new_data
from data.reader import read_daily_data_df
from files.keys import get_json_key
from files.s3 import download_file, file_last_modified_timestamp


def _updated_today(date: Optional[datetime.datetime]) -> bool:
    return date and gmtime().tm_mday == date.day


app = FastAPI()

print("About to read in full df")
# df = read_daily_data_df()
print("Done reading in full df")


@app.get("/charts/mayer_multiple/{ticker}/png")
def get_data_for_ticker(ticker: str):
    # print(ticker)
    logging.debug(f"Retrieving data for {ticker}.")
    key = get_json_key(ticker)
    date = file_last_modified_timestamp(key)
    local_file = f"/tmp/{ticker}.cache"
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
