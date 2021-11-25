import requests
import json
from datetime import date, timedelta

search_date = date.today() + timedelta(days=-1)

api_key = 'jxuqkztm9pecwva837ag7wya'
access_level = 'trial'
version = 'v7'
language_code = 'ru'
year = search_date.strftime('%Y')
month = search_date.strftime('%m')
day = search_date.strftime('%d')
format = 'json'

url = f'https://api.sportradar.us/nhl/{access_level}/{version}/{language_code}/games/{year}/{month}/{day}/schedule.{format}'
params = {'api_key': api_key}

json_d = requests.get(url, params).json()

with open(f'NHL_{year}{month}{day}.json', 'w') as outfile:
    outfile.write(json.dumps(json_d, indent=4))