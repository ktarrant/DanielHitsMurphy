from plotly import plotly
from plotly.tools import get_embed, make_subplots, FigureFactory as FF
from download import get_gamelog_cached
from datetime import datetime
import pandas as pd
import numpy as np
import re

def create_weekly(wpaCum):
    weeks = pd.date_range(
        start=wpaCum.index[0], end=wpaCum.index[-1],
        freq='7D')
    for week_id in range(len(weeks)):
        start_date = weeks[week_id]
        if week_id + 1 == len(weeks):
            end_date = datetime.today()
        else:
            end_date = weeks[week_id + 1]
        data = wpaCum[start_date:end_date]
        if len(data) > 0:
            yield {
                "start_date": start_date,
                "end_date": end_date,
                "Open" : data.iloc[0],
                "Close" : data.iloc[-1],
                "High" : data.max(),
                "Low" : data.min(),
                }

def make_candlestick(gamelog, column, reduce_func=None):
    base_series = gamelog.set_index("Date")[column]
    if reduce_func:
        series = reduce_func(base_series).dropna()
    else:
        series = base_series.cumsum().dropna()
    weekdata = list(create_weekly(series))
    weeks = pd.DataFrame(weekdata).dropna()
    fig = FF.create_candlestick(weeks.Open, weeks.High, weeks.Low, weeks.Close,
        dates=weeks.start_date)
    fig['layout'].update(height=600, width=600, title=column)
    return fig

badEggRe = re.compile(r"(\([0-9]+\))")
cleanEgg = (lambda val: None if isinstance(val, float) else ("2016 " + badEggRe.sub("", str(val))))
gamelog = get_gamelog_cached().dropna()
gamelog.Date = gamelog.Date.apply(cleanEgg)
gamelog.Date = pd.to_datetime(gamelog.Date)

wpa_trace = make_candlestick(gamelog, "WPA")
obp_trace = make_candlestick(gamelog, "OBP", reduce_func=pd.expanding_mean)
traces = [wpa_trace, obp_trace]
html = ""
for i in range(len(traces)): 
    trace = traces[i]
    url = plotly.plot(trace, filename='murphy-candlestick-{}'.format(i), auto_open=True)
    html += get_embed(url)

with open("index.html", "w") as fobj:
    fobj.write(html)