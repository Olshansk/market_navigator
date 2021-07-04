import datetime


def zscore(x, window):
    r = x.rolling(window=window)
    m = r.mean().shift(1)
    s = r.std(ddof=0).shift(1)
    z = (x - m) / s
    return z


def compute_mm_metrics_for_ticker(df_full, ticker, window=200):
    df = df_full[df_full.ticker == ticker].copy()
    if len(df) == 0:
        return None

    df["price_roll_avg_200"] = df["price"].rolling(window).mean()
    df["mayer_multiple"] = df["price"] / df["price_roll_avg_200"]
    df["mm_z_score"] = zscore(df["mayer_multiple"], window)
    df["date"] = df.index
    df["freq_gt"] = (
        df["mayer_multiple"]
        .expanding()
        .apply(lambda s: s.iloc[:-1].gt(s.iloc[-1]).mean() * 100)
    )
    df = df[["price", "price_roll_avg_200", "mayer_multiple", "mm_z_score", "freq_gt"]]
    return df


TEXT = "{0}: The current Mayer Multiple is {1:.2f} with a {2} price of $USD {3:,.2f} and a 200 day moving average of ${4:,.2f} USD. The Mayer Multiple has historically been higher {5:,.2f}% of the time."


def format_message(df, ticker):
    last_row = df.iloc[-1]
    return TEXT.format(
        datetime.datetime.now(),
        last_row.mayer_multiple,
        ticker,
        last_row.price,
        last_row.price_roll_avg_200,
        last_row.freq_gt,
    )
