import logging
import json
import pandas as pd

from analysis.src.mayer_multiple.compute_metrics import (
    compute_mm_metrics_for_ticker, format_message)
from analysis.src.mayer_multiple.plot_metrics import build_mm_histogram
from api.files.keys import get_json_key, get_png_key
from api.files.s3 import upload_file

def compute_new_data(ticker: str, df: pd.DataFrame):
    logging.debug(f"About to try computing data for {ticker}...")
    df = compute_mm_metrics_for_ticker(df, ticker)
    if df is None:
        logging.error(f"Data for {ticker} does not exist.")
        return False
    logging.debug(f"About to start computing data for {ticker}...")
    message = format_message(df, ticker)
    chart, _ = build_mm_histogram(df)

    # PNG upload
    png_key = get_png_key(ticker)
    png_filename = f"/tmp/{png_key}"
    chart.save(png_filename)
    png_url = upload_file(png_filename, key=png_key)

    # JSON upload
    json_key = get_json_key(ticker)
    json_filename = f"/tmp/{json_key}"
    data = {"message": message, "chart": chart.to_json(), "png": png_url}
    with open(json_filename, "w") as f:
        json.dump(data, f)
    upload_file(json_filename, key=json_key)

    return True
