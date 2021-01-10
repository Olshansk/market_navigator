# https://altair-viz.github.io/gallery/multiline_tooltip.html
import altair as alt
import pandas as pd

def get_min_max_plot(df, delta):
    ax = df.plot(color=[RED, BLUE], figsize=(20,10))
    ax.set_title(f"Percentage of stocks within {int(delta * 100)}% of 52 week min/max.")
    ax.set_xlabel("")
    ax.axhline(y=df['near_max'].mean(), linestyle='--', color=RED)
    ax.axhline(y=df['near_min'].mean(), linestyle='--', color=BLUE)
