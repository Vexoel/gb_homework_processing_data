from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from pprint import pprint

LOGIN = 'study.ai_172@mail.ru'
PASSWORD = 'NextPassword172#'

def add_news(p_collection, p_vacancy):
    try:
        p_collection.insert_one(p_vacancy)
    except DuplicateKeyError as e:
        pass

chrome_options = Options()
chrome_options.add_argument("start-maximized")

driver = webdriver.Chrome('chromedriver.exe', options=chrome_options)

driver.get('https://account.mail.ru/')

wait = WebDriverWait(driver, 5)
button = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class = "submit-button-wrap"]//button')))

element = driver.find_element(By.XPATH, '//div[contains(@class, "auto")]/input[@name = "username"]')
element.send_keys(LOGIN)

button.click()

wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class = "change-link"]')))

element = driver.find_element(By.XPATH, '//div[contains(@class, "auto")]/input[@name = "password"]')
element.send_keys(PASSWORD)

button = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class = "submit-button-wrap"]//button')))
button.click()

wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Входящие")]')))

href = ""
links = set()

while True:
    elements = driver.find_elements(By.XPATH,
                                    '//a[contains(@class, "js-tooltip-direction_letter-bottom js-letter-list-item")]')

    for element in elements:
        links.add(element.get_attribute('href'))

    if href == elements[-1]:
        break
    else:
        href = elements[-1]

    actions = ActionChains(driver)
    actions.move_to_element(elements[-1]).perform()

mails = []

count = 0

for link in links:
    item = {}
    driver.get(link)

    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="letter__footer-button"]//span[text() = "Ответить"]')))

    element = driver.find_element(By.XPATH, '//div[@class = "letter__author"]/span[@class = "letter-contact"]')
    item['from'] = element.text
    element = driver.find_element(By.XPATH, '//div[@class="letter__author"]/div[@class = "letter__date"]')
    item['date'] = element.text
    element = driver.find_element(By.XPATH, '//h2[@class="thread__subject"]')
    item['subject'] = element.text
    element = driver.find_element(By.XPATH, '//div[@class="letter-body__body-content"]//div[contains(@id, "BODY")]')
    item['body'] = element.text

    mails.append(item)
    count += 1
    if count == 5:
        break;

client = MongoClient('127.0.0.1', 27017)

db = client['emails']

mailru = db.mailru

for email in mails:
    add_news(mailru, email)

for n in mailru.find():
    pprint(n)