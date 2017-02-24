import csv
import datetime
import plotly
import plotly.graph_objs as go
import pandas as pd
import math
import os.path


def filter_csv_for_date_range(file_name, start_date, end_date):
    """
    Given the terror-database-csv,
    we want to filter data to get a list of dictionaries
    containing the date (iyear, imonth, iday), the country (country_txt)
    and the casulties (nkill + nwound)
    """
    f = open(file_name,"r", encoding="latin1")
    reader = csv.DictReader(f, delimiter=",", quotechar='"')

    terror_attacks = list()
    for row in reader:
        if not int(row["imonth"]) == 0:
            year = int(row["iyear"])
            if int(row["iday"]) == 0:
                day = 1
            else:
                day = int(row["iday"])
            month = int(row["imonth"])
            attack_date = datetime.datetime(year, month, day)
            if attack_date >= start_date and attack_date < end_date + datetime.timedelta(days=1):
                attack = dict()
                attack["date"] = datetime.datetime(day=1,
                                                   month=month,
                                                   year=year)
                attack["country"] = row["country_txt"]

                if row["nwound"] == "":
                    nwound = 0
                else:
                    nwound = float(row["nwound"].replace(',', '.'))
                if row["nkill"] == "":
                    nkill = 0
                else:
                    nkill = float(row["nkill"].replace(',', '.'))
                attack["casulties"] = nwound + nkill
                terror_attacks.append(attack)
    f.close()
    return terror_attacks

def get_countries_in_europe_from_data(terror_attacks):
    attacked_countries = set()
    for attack in terror_attacks:
        attacked_countries.add(attack["country"])
    # we got all countries now, moving on to dbpedia
    countries_file_name = "countries_europe.txt"

    in_europe = set()
    if not os.path.exists(countries_file_name):
        sparql = SPARQLWrapper("http://dbpedia.org/sparql")
        sparql.setReturnFormat(JSON)

        for country in attacked_countries:
            query = "ASK {?country rdfs:label '%s'@en. ?country rdf:type yago:WikicatCountriesInEurope.}" % country
            sparql.setQuery(query)
            query_json = sparql.query().convert()
            if query_json["boolean"]:
                in_europe.add(country)
        with open(countries_file_name, "w") as countries_file:
            for country in in_europe:
                countries_file.write(country + "\n")
    return in_europe


def filter_by_country_list(terror_attacks, country_set):
    terror_attacks_filtered = list()
    for attack in terror_attacks:
        if attack["country"] in country_set:
            terror_attacks_filtered.append(attack)
    return terror_attacks_filtered


def generate_data_frame(terror_attacks):
    casulties_list = list()
    date_list = list()
    for attack in terror_attacks:
        casulties_list.append(attack["casulties"])
        date_list.append(attack["date"])
    # First create an empty dataframe
    df = pd.DataFrame()
    # Create a column from the datetime variable
    df["datetime"] = date_list
    df["datetime"] = pd.to_datetime(df["datetime"])
    df.index = df["datetime"]
    df["casulties"] = casulties_list
    return df

#grouped_dates = df.resample("M").sum()
#grouped_dates = grouped_dates.fillna(0)
#grouped_dates


#timestamp_dict = grouped_dates.to_dict()
#timestamp_dict = timestamp_dict["casulties"]
#timestamp_dict
