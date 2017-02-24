import requests
import json
import sys
from datetime import datetime
from calendar import monthrange
from dateutil.rrule import rrule, MONTHLY

import plotly
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot

plotly.offline.init_notebook_mode()

# Scheme to achieve: 
# http://api.zeit.de/content?q=release_date:[1960-01-01T00:00:00Z TO 1969-12-31T23:59:59.999Z]&fields=found
url = "http://api.zeit.de/content"
query = "release_date:[{date1} TO {date2}]"
fields = "found"
headers = { "X-Authorization" : "ef085f80d16fce2190406f102d5f38d354ca5014e803635c58d2"}

def get_article_count():
    count_dict = dict()
    for month in month_list(1, 2000, datetime.today().month, datetime.today().year):
        monthrange = get_first_and_last_day_of_month(datetime(day=month[0], month=month[1], year=month[2]))
        r = requests.get("{url}?q={query}".format(url=url, 
                                                  query=query.format(
                                                      date1=monthrange[0].isoformat("T") + "Z", 
                                                      date2=monthrange[1].isoformat("T") + "Z")), 
                                                  headers=headers)
        articles_json = r.json()
        count_dict[monthrange[1]] = articles_json["found"]
    return count_dict


def get_first_and_last_day_of_month(date):
    """
    This function returns, given a date, 
    a tuple with the first and last moment of the given dates' month.
    """
    first_day = datetime(day=1, month=date.month, year=date.year)
    
    last_day_number = monthrange(date.year, date.month)[1]
    last_day = datetime(day=last_day_number, month=date.month, year=date.year,
                        hour=23, minute=59, second=59, microsecond=999999)
    return (first_day, last_day)


def month_list(start_month, start_year, end_month, end_year):
    """ This function returns a list of months between to dates"""
    start = datetime(start_year, start_month, 1)
    end = datetime(end_year, end_month, 1)
    return [(d.day, d.month, d.year) for d in rrule(MONTHLY, dtstart=start, until=end)]

if __name__ == '__main__':
	xlist = list()
	ylist = list()
	article_count = get_article_count()
	for key in article_count.keys():
		xlist.append(key)
		ylist.append(article_count[key])
	data = [go.Scatter(x=xlist,y=ylist)]
	layout = go.Layout(
		title="Number of Articles on zeit.de about Terror since 2000",
		xaxis=dict(title="Year"),
		yaxis=dict(title="Number of article (grouped by month)"))
	fig = go.Figure(data=data, layout=layout)
	iplot(fig)

