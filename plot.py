from plotly import plotly
from plotly.tools import FigureFactory as FF
from matplotlib import pyplot
from download import get_gamelog_cached
from datetime import datetime
import pandas as pd
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
        yield {
            "start_date": start_date,
            "end_date": end_date,
            "Open" : data.iloc[0],
            "Close" : data.iloc[-1],
            "High" : data.max(),
            "Low" : data.min(),
            }

badEggRe = re.compile(r"(\([0-9]+\))")
cleanEgg = (lambda val: None if isinstance(val, float) else ("2016 " + badEggRe.sub("", str(val))))
gamelog = get_gamelog_cached()
gamelog.Date = gamelog.Date.apply(cleanEgg)
gamelog.Date = pd.to_datetime(gamelog.Date)
wpaCum = gamelog.set_index("Date").WPA.cumsum().dropna()
weeks = pd.DataFrame(create_weekly(wpaCum))
fig = FF.create_candlestick(weeks.Open, weeks.High, weeks.Low, weeks.Close, dates=weeks.start_date)
plotly.plot(fig, filename='murphy-candlestick', validate=False)
# pyplot.plot(wpaCum)
# pyplot.show()