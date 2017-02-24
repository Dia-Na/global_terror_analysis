import plotly
import plotly.graph_objs as go
import json
import pandas as pd
import datetime
from SPARQLWrapper import SPARQLWrapper, JSON
import os.path

#init_notebook_mode(connected=True)

def get_json_data(filename):
    with open(filename, "r") as f:
        terror_json = json.load(f)
    return terror_json


def get_german_cities(terror_json):
    # We have the data, now we want to get the list of dates with terror-news for germany
    # BUT: There is no location-entry for Germany/Deutschland
    # Solution:       Get location and ask DBpedia if it is located in Germany
    #
    # Real solution:  Look if you can find "cities_germany.txt".
    #                 If not, fetch it from DBpedia and create that file.
    cities_file_name = "cities_germany.txt"

    in_germany = set()
    if not os.path.exists(cities_file_name):
        sparql = SPARQLWrapper("http://dbpedia.org/sparql")
        sparql.setReturnFormat(JSON)


        # we don't want to make too much queries, so make a set of all locations (unique!)
        locations = set()
        for entry in terror_json:
            for keyword in entry["keywords"]:
                if keyword["rel"] == "location":
                    locations.add(keyword["name"])
        for location in locations:
            query = "ASK {?city rdfs:label '%s'@de. ?city dbo:country dbr:Germany.}" % location #fuck .format
            sparql.setQuery(query)
            query_json = sparql.query().convert()
            if query_json["boolean"]:
                in_germany.add(location)
        with open(cities_file_name, "w") as cities_file:
            for city in in_germany:
                cities_file.write(city + "\n")


    # Now that we are sure that "cities_germany.txt" exists, we can load it in.
    with open(cities_file_name, "r") as cities_file:
        for line in cities_file:
            in_germany.add(line.rstrip("\n"))
    return in_germany

def filter_data_for_mentioned_cities(json, set_of_cities):
    date_list = list()

    for entry in json:
        city_in_list = False
        for keyword in entry["keywords"]:
            if keyword["name"] in set_of_cities:
                city_in_list = True
        if city_in_list:
            date = datetime.datetime.strptime(entry["release_date"].split("T")[0], "%Y-%m-%d")
            date_list.append(date)
    return date_list

def json_to_date_list(json):
    date_list = list()
    for entry in json:
        date = datetime.datetime.strptime(entry["release_date"].split("T")[0], "%Y-%m-%d")
        date_list.append(date)
    return date_list


def filter_for_date_range(date_list, start_date, end_date):
    """
    Filters a list of dates (datetime-format) to a range of a given start- and end-date.

    >>> filter_for_date_range([     datetime.datetime(2000, 1, 1, 0, 0),
                                    datetime.datetime(2000, 1, 2, 0, 0),
                                    datetime.datetime(2000, 1, 3, 0, 0),
                                    datetime.datetime(2000, 1, 4, 23, 59),
                                    datetime.datetime(2000, 1, 5, 0, 0)
                              ],
                              datetime.datetime(2000,1,2), # start-date
                              datetime.datetime(2000,1,4)) # end-date
    [datetime.datetime(2000, 1, 2, 0, 0), datetime.datetime(2000, 1, 3, 0, 0),datetime.datetime(2000, 1, 4, 23, 59)]

    """
    dates_in_range = list()
    for date in date_list:
        if date >= start_date and date < end_date + datetime.timedelta(days=1):
            dates_in_range.append(date)
    return dates_in_range

def generate_data_frame(dates):
    # Now we want to group this. Easily done by pandas
    # First create an empty dataframe
    df = pd.DataFrame()
    # Create a column from the datetime variable
    df["datetime"] = dates
    df["datetime"] = pd.to_datetime(df["datetime"])
    df.index = df["datetime"]
    return df


def create_scatter_plot_from_date_dict(timestamp_dict, plot_name, type="scatter"):
    xlist = list()
    ylist = list()
    for key in timestamp_dict.keys():
        xlist.append(key)
        ylist.append(timestamp_dict[key])
    if type=="scatter":
        scatter = go.Scatter(x=xlist,y=ylist, name=plot_name)
    else:
        scatter = go.Bar(x=xlist,y=ylist, name=plot_name)
    return scatter
