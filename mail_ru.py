"""
1) Написать программу, которая собирает входящие письма из своего или тестового почтового ящика и сложить данные
о письмах в базу данных (от кого, дата отправки, тема письма, текст письма полный)
"""

import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError as dke
from datetime import date, timedelta

chrome_options = Options()
chrome_options.add_argument('start-maximized')

from datetime import date, timedelta

# ИНИЦИАЛИЗАЦИЯ

driver = webdriver.Chrome(executable_path='./chromedriver.exe', options=chrome_options)

driver.get('https://mail.ru/')
driver.implicitly_wait(10)

actions = ActionChains(driver)

def login_to_mail(log, pswd):

    elem = driver.find_element(By.NAME, 'login')
    elem.send_keys(log)

    enter_button = driver.find_element(By.XPATH, "//input[@id='saveauth']")
    enter_button.click()

    enter_button = driver.find_element(By.XPATH, "//button[@data-testid='enter-password']")
    enter_button.click()

    elem = driver.find_element(By.NAME, 'password')
    elem.send_keys(pswd)

    enter_button = driver.find_element(By.XPATH, "//button[@data-testid='login-to-mail']")
    enter_button.click()

login_mail = "study.ai_172@mail.ru"
password_mail = "NextPassword172#"
login_to_mail(login_mail, password_mail)


driver.switch_to.default_content()
driver.implicitly_wait(10)

# ОСНОВНОЙ ЦИКЛ - ОБРАБОТКА ПОЧТЫ


letter_urls = set()
last_len = 0
#получение всех ссылок
while True:
    letters = driver.find_elements(By.XPATH, "//a[contains(@class, 'js-letter-list-item')]")
    letter_urls.update(letter.get_attribute("href") for letter in letters)
    if last_len == len(letter_urls):
        break

    last_len = len(letter_urls)

    actions = ActionChains(driver)
    actions.move_to_element(letters[-1])
    actions.perform()
    time.sleep(1)

result_items = []

for letter_url in letter_urls:
    item ={}
    driver.get(letter_url)
    item["url"] = letter_url
    item["title"] = driver.find_element(By.XPATH, "//h2[contains(@class, 'thread__subject')]").text
    container = driver.find_element(By.XPATH, "//div[contains(@class, 'thread__letter')][1]")


    item["body"] = container.find_element(By.XPATH, ".//div[contains(@class, 'letter__body')]").text
    item["from"] = container.find_element(By.XPATH, "//span[contains(@class, 'letter-contact')]").get_attribute('title')
    item["date"] = container.find_element(By.XPATH, "//div[contains(@class, 'letter__date')]").text
    if 'сегодня' in item["date"]:
        item["date"] = item["date"].replace("сегодня", date.today())
    if 'вчера' in item["date"]:
        item["date"] = item["date"].replace("вчера", date.today() - timedelta(days=1))

    result_items.append(item)

driver.close()

# СЛОЖИТЬ ВСЮ ПОЧТУ В БД

client = MongoClient('127.0.0.1', 27017)
db = client['mails_db']
mails_db = db.mails

for item in result_items:
    mails_db.update_one({'link': item['url']}, {'$set': item}, upsert=True)