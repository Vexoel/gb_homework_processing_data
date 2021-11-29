import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json

def str_to_float(p_str):
  try:
    n = float(p_str)
  except:
    n = None
  return n

def parse_val(p_str):
  min = ''
  max = ''
  cur = ''
  scnd = False
  
  for str in p_str.split():
    if str == 'от':
      scnd = False
    else:
      if str == 'до':
        scnd = True
      else:
        if str == 'Ц':
          scnd = True
        else:
          n = str_to_float(str)
          if n is None:
            cur += str
          else:
            if scnd:
              max = max + str
            else:
              min = min + str
  return {'min': str_to_float(min), 'max': str_to_float(max), 'cur': cur}


site = 'hh.ru'

url = 'https://hh.ru/search/vacancy'

job = input('¬ведите должность дл€ поиска: ')

try:
  pages = int(input('¬ведите введите кол-во страниц разбора: '))
except:
  pages = 1

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}

dict = []

for n in range(1, pages + 1):
  params = {'text': job, 'page': n}
  
  responce = requests.get(url, params=params, headers=headers)
  
  dom = BeautifulSoup(responce.text, 'html.parser')
  
  items = dom.find_all('div', class_='vacancy-serp-item__row vacancy-serp-item__row_header')
  
  for item in items:
    i = {}
    i['site'] = site
    i['job'] = item.find('a', class_='bloko-link').text
    str = item.find('a', class_='bloko-link').get('href')
    i['link'] = urljoin(str, urlparse(str).path)
    
    div = item.find('div', class_='vacancy-serp-item__sidebar')
    
    if div is None:
      v = {'min': None, 'max': None, 'cur': None}
    else:
      str = div.findChildren('span' , recursive=False)[0].text
      v = parse_val(str)
    
    i['salary'] = v
    
    dict.append(i)

json_vacancy = json.dumps(dict, ensure_ascii=False, indent=4)

with open(f'{site}_{job}.json', 'w') as outfile:
    outfile.write(json_vacancy)
