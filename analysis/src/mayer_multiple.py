import datetime
import json
import os
import socket
from collections import OrderedDict
from datetime import timedelta

import sys
import dropbox
import numpy
import requests
import requests_cache
import tweepy
from apscheduler.schedulers.blocking import BlockingScheduler

TIMESERIES_HISTOGRAM_NAME="mayer_multiple_timeseries_histogram.png"

import graphs

def is_dev():
    return os.getenv("ENVIROMENT") == "DEV"

if is_dev():
    # @OlshTest - Use for manual testing
    CONSUMER_KEY = "H5Fn9jBEMDrlV03UvguTDDt8p"
    CONSUMER_SECRET = "x3582fsPTuJ0l6QSGXopBvIhtB0grvoUeCsgwJQ86qcJQF3p2L"
    ACCESS_KEY = "1343059956036218880-4UzlRYXcmXJp3XxJrFaudTJbBcEFDI"
    ACCESS_SECRET = "aYgxQqGvJcQquw2VcObD4QxOaKvM5y9eLld3GpwCi5k7M"
else:
    # @TIPMayerMultple - Use for production
    CONSUMER_KEY = "AZYrQ8jryRXFojAsQSrzis7VZ"
    CONSUMER_SECRET = "nmkDgqRA1heR2UEnHsguJdjSQDkawHhUSz2POz5okGNBgRcbbQ"
    ACCESS_KEY = "938285416591056896-OIOm5pG0cYTOVds1wlRHQQnnU7RMe9b"
    ACCESS_SECRET = "8NREjrRzTQbapdU7GXfk0DNbhqVwqXNd98ljXZffTssdt"

# Dropbox
DROPBOX_APP_KEY = "agio191eo12ypap"
DROPBOX_APP_SECRET = "xnj7wwvamwspvm0"
DROPBOX_ACCESS_TOKEN = "v6bQXa8poV0AAAAAAABJYrtEohZ_D8W_AQNlPuK-V-Lk6fAyblHVGNCrxICNGYGe"

HISTORICAL_PRICE_ENDPOINT = 'https://api.coindesk.com/v1/bpi/historical/close.json?start={}&end={}'
CURRENT_PRICE_ENDPOINT = 'https://api.coindesk.com/v1/bpi/currentprice.json'

TWEET_FORMAT = "{0}: The current Mayer Multiple is {1:.2f} with a $BTC price of $USD {2:,.2f} and a 200 day moving average of ${3:,.2f} USD. The @TIPMayerMultple has historically been higher {4:,.2f}% of the time with an average of {5:,.2f}. Learn more at: MayerMultiple.com"

# if socket.gethostname() == 'Daniels-MacBook-Pro.local':
#     requests_cache.install_cache('cache')

# Returns a dict of string-float pairs representing the date and mayer multiple
# at any point in time. For example: {'2018-04-12': 0.8278496457529817}
def compute_historical_mayer_multiples():
    first_date = datetime.date(year=2010, month=7, day=17) # I manually found that this is the earliest day for which data is available
    today = datetime.date.today()

    historical_data = requests.get(HISTORICAL_PRICE_ENDPOINT.format(first_date, today)).json()
    values = list(historical_data['bpi'].values())
    dates = list(historical_data['bpi'].keys())

    multiples_history = {}

    for idx in range(len(values))[200:]:
        avg = numpy.mean(values[idx - 200:idx])
        multiple = values[idx] / avg
        multiples_history[dates[idx]] = multiple

    return multiples_history

# Returns the most recent price of BTC available
def get_current_price():
    return requests.get(CURRENT_PRICE_ENDPOINT).json()['bpi']['USD']['rate_float']

# Returns the most recent 200 day moving average price of BTC
def get_200_day_moving_average():
    today = datetime.date.today()
    today_string = today.strftime("%Y-%m-%d")

    today_minus_200_days = today - timedelta(days=200)
    today_minus_200_days_string = today_minus_200_days.strftime("%Y-%m-%d")

    historical_data = requests.get(HISTORICAL_PRICE_ENDPOINT.format(today_minus_200_days_string, today_string)).json()

    return numpy.mean(list(historical_data['bpi'].values()))

# Formats the TWEET_FORMAT string given the inputs provides and tweets it out!
def tweet(mayer_multiple, current_price, moving_avg_200_days, frequency, average):
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, 'http:localhost')
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth)

    now = datetime.datetime.now()
    now = now.strftime("%b %d, %Y")

    tweet = TWEET_FORMAT.format(now, mayer_multiple, current_price, moving_avg_200_days, frequency, average)

    media_ret = api.media_upload(TIMESERIES_HISTOGRAM_NAME)
    api.update_status(status=tweet, media_ids=[media_ret.media_id])

def get_frequency(mayer_multiple, multiples_history):
    return (len([x for x in multiples_history if x >= mayer_multiple]) / len(multiples_history)) * 100

def upload_graph(filename, dbx):
    with open(filename, "rb") as f:
        dbx.files_upload(f.read(), '/{}'.format(filename), mute=True,  mode=dropbox.files.WriteMode.overwrite)

def upload_graphs(multiples_history_dict, mayer_multiple_today):
     multiples_history_dict_one_year = dict(list(OrderedDict(sorted(multiples_history_dict.items(), key=lambda t: t[0])).items())[-365:])
     graphs.mayer_multiple_timeseries(multiples_history_dict, "mayer_multiple_timeseries_all_time.png")
     graphs.mayer_multiple_timeseries(multiples_history_dict_one_year, "mayer_multiple_timeseries_one_year.png")

     multiples_history = list(multiples_history_dict.values())
     graphs.mayer_multiple_histogram(multiples_history, round(mayer_multiple_today, 2), TIMESERIES_HISTOGRAM_NAME)

     dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
     upload_graph("mayer_multiple_timeseries_all_time.png", dbx)
     upload_graph(TIMESERIES_HISTOGRAM_NAME, dbx)
     upload_graph("mayer_multiple_timeseries_one_year.png", dbx)

sched = BlockingScheduler()

@sched.scheduled_job('interval', hours=6)
def timed_job():
    current_price = get_current_price()
    moving_avg_200_days = get_200_day_moving_average()
    mayer_multiple = current_price / moving_avg_200_days

    multiples_history_dict = compute_historical_mayer_multiples()
    multiples_history = list(multiples_history_dict.values())
    frequency = get_frequency(mayer_multiple, multiples_history)
    mayer_multiple_avg = numpy.mean(multiples_history)

    upload_graphs(multiples_history_dict, mayer_multiple)
    tweet(mayer_multiple, current_price, moving_avg_200_days, frequency, mayer_multiple_avg)
