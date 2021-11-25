import requests
import json

user = 'vexoel'
url = f'https://api.github.com/users/{user}/repos'
params = {'type': 'public'}

json_d = requests.get(url, params).json()

for j in json_d:
    print(j['name'])

with open(f'{user}.json', 'w') as outfile:
    outfile.write(json.dumps(json_d, indent=4))