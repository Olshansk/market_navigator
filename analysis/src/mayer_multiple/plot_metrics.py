import altair as alt
import pandas as pd
import numpy as np

def _bin_data(df: pd.DataFrame, bin_size: float = 0.05):
    bins = np.arange(0, 3, bin_size)
    bin_labels = [round(b + bin_size/2,3) for b in bins][:-1]
    df['bin'] = pd.cut(df['mayer_multiple'], bins, labels=bin_labels)
    return pd.DataFrame(df.groupby('bin').bin.count()).rename(columns={'bin': 'freq'}).reset_index()


def _filter_data(data: pd.DataFrame):
    first_index = data[data['freq'].gt(0)].index[0]
    data_filtered = data.iloc[first_index:]
    last_index = data_filtered[data_filtered.freq.eq(0)].index[0]
    first_index = 0 if first_index == 0 else first_index - 1
    last_index = last_index if len(data) == last_index else last_index + 1
    return data[first_index:last_index]

def build_mm_histogram(df: pd.DataFrame):
    bin_size = 0.05

    data = _bin_data(df, bin_size)
    data = _filter_data(data)

    data['bin'] = data['bin'].astype('float64')
    data['bin_max'] = data['bin'].shift(-1).fillna(data['bin'].max() + 0.05)

    # The basic bar chart
    bar = alt.Chart(data).mark_bar().encode(
        x=alt.X('bin', bin='binned', title='mayer multiple'),
        x2='bin_max',
        y='freq')

    # Add vertical lines with text and thresholds
    current_mm = round(df.iloc[-1].mayer_multiple, 2)
    vertline_data = pd.DataFrame({
        'value': [current_mm],
        'label':['today']
    })
    vertline = alt.Chart(vertline_data).mark_rule(
        color='red',
        strokeWidth=2
    ).encode(x='value')
    vertline_text = alt.Chart(vertline_data).mark_text(
        align='left', dx=5, dy=-5
    ).encode(
        x='value', text='label')

    # Create a selection that chooses the nearest point & selects based on x-value
    nearest = alt.selection(
        type='single',
        nearest=True,
        on='mouseover',
        fields=['bin'],
        empty='none')

    # Transparent selectors across the chart. This is what tells us
    # the x-value of the cursor
    selectors = alt.Chart(data).mark_point().encode(
        x='bin',
        opacity=alt.value(0),
    ).add_selection(
        nearest
    )

    # Draw points on the line, and highlight based on selection
    points = bar.mark_point().encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0)),
        color=alt.value('red')
    )

    # Draw text labels near the points, and highlight based on selection
    points_text = bar.mark_text(align='left', dx=5, dy=-5).encode(
        text=alt.condition(nearest, 'freq:Q', alt.value(' '))
    )

    # Put all the layers into a chart and bind the data
    chart = alt.layer(bar, selectors, points, points_text, vertline, vertline_text).encode(x=alt.X('x:Q', title='test')).properties(
        width=600, height=300
    )

    return (chart, data)