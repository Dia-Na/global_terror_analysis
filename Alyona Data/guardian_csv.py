#!/usr/bin/python

# how to use: 
#	python zeit_api.py <name of the json to store>

import requests
import json
import sys
import csv
from datetime import datetime

url = "http://content.guardianapis.com/search?from-date={from_date}&to-date={to_date}&page-size={page_size}&q={keyword}&api-key={api_key}&page={page}"
terror_keywords = ["terror"]
api_key = "0a574213-87b3-495e-8355-e9391049dab1" # you have to enter one!!
page_size = 200
page = 1
from_date = "2000-01-01"
to_date = "2016-12-31"

def get_results():
	"""
	Parses zeit.de-API via REST-calls, cleans it and returns the resulting JSON.
	"""
	all_terror_data = []
	for keyword in terror_keywords:
		print("Fetching data for keyword '{}'.".format(keyword))

		# call REST-API of zeit.de, scheme: http://api.zeit.de/keyword/<keyword>
		# header for authorization
		# parameter to set limit and offset
		page = 1
		r = requests.get(url.format(from_date=from_date, to_date=to_date, page_size=page_size, keyword=keyword, api_key=api_key, page=page))
		terror_json = r.json()
		terror_json = terror_json["response"]

		# data could be larger than maximum limit, do more calls with offset
		page_count = int(terror_json["pages"])
		print("{} pages found".format(page_count))
		
		while page < page_count:
			page = page + 1
			print("Loading page {}".format(page))
			r = requests.get(url.format(from_date=from_date, to_date=to_date, page_size=page_size, keyword=keyword, api_key=api_key, page=page))
			offset_data = r.json()
			offset_data = offset_data["response"]
			
			# concatenate the list in 'matches'
			terror_json["results"] = terror_json["results"] + offset_data["results"]

		# we don't want every information, just the articles (located in 'matches')
		all_terror_data = all_terror_data + terror_json["results"]
		
	all_terror_data = clean_data(all_terror_data)
	return all_terror_data


def clean_data(json):
	"""
	Calls methods to remove duplicates und converts dates to "yyyy-mm-dd".
	"""
	json = remove_duplicates(json)
	for article in json:
		article["webPublicationDate"] = convert_date(article["webPublicationDate"])
	return json

def remove_duplicates(json):
	"""
	Removes duplicates, i.e. articles with the same 'uuid'.
	"""
	seen = dict()
	for d in json:
		uuid = d["id"]
		if uuid not in seen:
			seen[uuid] = d
	return list(seen.values())

def convert_date(date_str):
	"""
	Converts dates from '%Y-%m-%dT%X.<ms>Z' and
	'%Y-%m-%dT%XZ' to '%Y-%m-%d' or 'yyyy-mm-dd'.
	"""
	date_str = date_str.split(".")[0].split("Z")[0]
	date_obj = datetime.strptime(date_str, "%Y-%m-%dT%X")
	return date_obj.strftime("%Y-%m")


def get_article_data(all_terror_data):
	"""
	With all article-data and the titles, we also want to have the keywords.
	So we have to call every article and get the keywords. The are appended to the original JSON-object.
	"""
	call_counter = 0
	print("Fetching keywords for every article.")
	print("{} REST-calls needed.".format(len(all_terror_data)))
	for article in all_terror_data:
		uri = article["uri"]
		r = requests.get(uri, headers=headers)
		article_json = r.json()
		article["keywords"] = article_json["keywords"]
		call_counter += 1
		if call_counter % 100 == 0:
			print("Made {} calls.".format(call_counter))
	return all_terror_data
	
def count_articles_per_month(all_terror_data):
	months = dict()
	for article in all_terror_data:
		date = article["webPublicationDate"]
		if date not in months:
			months[date] = 1
		else:
			months[date] = months[date] + 1
	return months


# "main method", calls above get_results()-method and invokes it with first parameter.
if __name__ == '__main__':
	all_terror_data = get_results()
	articles_per_month = count_articles_per_month(all_terror_data)
	#print(articles_per_month)
	with open(sys.argv[1], 'w') as file:
		file.write("month;count\n")
		for month in articles_per_month:
			file.write("{month};{count}\n".format(month=month, count=articles_per_month[month]))
	
	#all_terror_data = get_article_data(all_terror_data)
	#with open(sys.argv[1], 'w') as f:
	#	json.dump(all_terror_data, f, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=True)
