import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from pprint import pprint
import json


# функция безопасного перевода str в float
def str_to_float(p_str):
    try:
        num = float(p_str)
    except ValueError:
        num = None

    return num


# функция разбора вилки зп
def parse_salary(p_str):
    min_salary = ''
    max_salary = ''
    currency_salary = ''
    is_max_salary = False

    for str_item in p_str.split():
        if str_item == 'от':
            is_max_salary = False
        elif str_item == 'до':
            is_max_salary = True
        elif str_item == '–':
            is_max_salary = True
        else:
            num = str_to_float(str_item)

            if num is None:
                currency_salary += str_item
            elif is_max_salary:
                max_salary += str_item
            else:
                min_salary += str_item

    return {'min_salary': str_to_float(min_salary), 'max_salary': str_to_float(max_salary), 'currency': currency_salary}


# функция получения списка вакансий с сайта hh.ru
def get_vacancy_list(p_vacancy, p_page):
    site = 'hh.ru'

    url = 'https://hh.ru/search/vacancy'

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}

    params = {'text': p_vacancy}

    dict_vacancy = []

    for n in range(1, p_page + 1):
        params['page'] = n

        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 404:
            break

        dom = BeautifulSoup(response.text, 'html.parser')

        items = dom.find_all('div', class_='vacancy-serp-item__row vacancy-serp-item__row_header')

        for item in items:
            vacancy = {'site': site, 'job': item.find('a', class_='bloko-link').text}

            link = item.find('a', class_='bloko-link').get('href')

            vacancy['link'] = urljoin(link, urlparse(link).path)

            vacancy['_id'] = vacancy['link'].split('/')[-1]

            div = item.find('div', class_='vacancy-serp-item__sidebar')

            if div is None:
                salary = {'min_salary': None, 'max_salary': None, 'currency': None}
            else:
                salary = parse_salary(div.findChildren('span', recursive=False)[0].text)

            vacancy['salary'] = salary

            dict_vacancy.append(vacancy)

    return dict_vacancy


# функция добавления записи в MongoDB
def add_vacancy(p_collection, p_vacancy):
    try:
        p_collection.insert_one(p_vacancy)
    except DuplicateKeyError as e:
        pass


# функция поиска вакансий по ЗП
def find_vacancy(p_collection, p_salary):
    dict_vacancy = []

    for vacancy in p_collection.find(
            {
                '$or':
                    [
                        {
                            'salary.min_salary': {'$gt': p_salary}
                        },
                        {
                            'salary.max_salary': {'$gt': p_salary}
                        }
                    ]
            }
    ):
        dict_vacancy.append(vacancy)

    return dict_vacancy


# Запус сбора данных по вакансиям
job = input('Введите должность для поиска: ')

try:
    pages = int(input('Введите введите кол-во страниц разбора: '))
except ValueError:
    pages = 1

vacancy_list = get_vacancy_list(job, pages)


# Подключение и добавление в MongoDB
client = MongoClient('127.0.0.1', 27017)

db = client['vacancies']

vacancies = db.vacancies

for vacancy in vacancy_list:
    add_vacancy(vacancies, vacancy)


# Поиск по зп
dict_vacancy = find_vacancy(vacancies, 100000)

for vacancy in dict_vacancy:
    pprint(vacancy)


# Сохранение в JSON file всей БД (просто так)
vacancy_list = []

for vacancy in vacancies.find():
    vacancy_list.append(vacancy)

json_vacancy = json.dumps(vacancy_list, ensure_ascii=False, indent=4, sort_keys=True)

with open(f'{job}.json', 'w') as outfile:
    outfile.write(json_vacancy)