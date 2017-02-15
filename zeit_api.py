#!/usr/bin/python

# how to use: 
#	python zeit_api.py <name of the json to store>

import requests
import json
import sys
from datetime import datetime

url = "http://api.zeit.de/keyword"
terror_keywords = ["terroranschlaege", "terrorgefahr", "terrorismus", "islamistischer-terrorismus"]
headers = { "X-Authorization" : "<api-key>"} # you have to enter one!!
params = { "limit" : "1024" , "offset" : "0"}

def get_results():
	"""
	Parses zeit.de-API via REST-calls, cleans it and returns the resulting JSON.
	"""
	all_terror_data = []
	for keyword in terror_keywords:
		print("Fetching data for keyword '{}'.".format(keyword))
		params["offset"]="0"

		# call REST-API of zeit.de, scheme: http://api.zeit.de/keyword/<keyword>
		# header for authorization
		# parameter to set limit and offset
		r = requests.get("{url}/{keyword}".format(url=url, keyword=keyword), headers=headers, params=params)
		terror_json = r.json()

		# data could be larger than maximum limit, do more calls with offset
		data_parsed = int(params["limit"]) + int(params["offset"])
		data_found = int(terror_json["found"])
		while data_parsed < data_found:
			params["offset"] = str(data_parsed)
			r = requests.get("{url}/{keyword}".format(url=url, keyword=keyword), headers=headers, params=params)
			offset_data = r.json()
			
			# concatenate the list in 'matches'
			terror_json["matches"] = terror_json["matches"] + offset_data["matches"]
			data_parsed = int(params["limit"]) + int(params["offset"])

		# we don't want every information, just the articles (located in 'matches')
		all_terror_data = all_terror_data + terror_json["matches"]
	all_terror_data = clean_data(all_terror_data)
	return all_terror_data


def clean_data(json):
	"""
	Calls methods to remove duplicates und converts dates to "yyyy-mm-dd".
	"""
	json = remove_duplicates(json)
	for article in json:
		article["release_date"] = convert_date(article["release_date"])
	return json

def remove_duplicates(json):
	"""
	Removes duplicates, i.e. articles with the same 'uuid'.
	"""
	seen = dict()
	for d in json:
		uuid = d["uuid"]
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
	return str(date_obj.date())


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


# "main method", calls above get_results()-method and invokes it with first parameter.
if __name__ == '__main__':
	all_terror_data = get_results()
	all_terror_data = get_article_data(all_terror_data)
	with open(sys.argv[1], 'w') as f:
		json.dump(all_terror_data, f, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)
