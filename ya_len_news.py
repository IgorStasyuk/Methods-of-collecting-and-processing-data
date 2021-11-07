# Написать приложение, которое собирает основные новости с сайта на выбор news.mail.ru, lenta.ru, yandex-
# Для парсинга использовать XPath. Структура данных должна содержать:
# название источника;
# наименование новости;
# ссылку на новость;
# дата публикации.
# Сложить собранные новости в БД

import requests
from pprint import pprint
from lxml import html
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError as dke

client = MongoClient('127.0.0.1', 27017)

db = client['news_from_sites']
news_db = db.news

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}

lenta_url = 'https://lenta.ru'
response = requests.get(lenta_url)
dom = html.fromstring(response.text)
lenta_news = dom.xpath("//time[@class='g-time']/..")

def add_mongo_collection(name_collection, name_doc):
    try:
        name_collection.insert_one(name_doc)
    except dke:
        print(f"такая новость с _id {name_doc['_id']} уже занесена в базу")

len_news = []

for lenta_new in lenta_news:
    lenta_news_dict = {}

    name_news_lenta = str(lenta_new.xpath(".//time[@class='g-time']/../text()")[0])
    if '\xa0' in name_news_lenta:
        name_news_lenta = name_news_lenta.replace('\xa0', ' ')

    link_lenta = str(lenta_new.xpath(".//time[@class='g-time']/../@href")[0])
    if 'https:' not in link_lenta:
        link_lenta = lenta_url + link_lenta

    date_news = lenta_new.xpath(".//time[@class='g-time']/@datetime")

    lenta_news_dict['_id'] = link_lenta + name_news_lenta
    lenta_news_dict['source'] = 'Lenta.ru'
    lenta_news_dict['name_news_lenta'] = name_news_lenta
    lenta_news_dict['link_lenta'] = link_lenta
    lenta_news_dict['date_news'] = date_news
    len_news.append(lenta_news_dict)
    add_mongo_collection(news_db, lenta_news_dict)

pprint(len_news)


yandex_url = 'https://yandex.ru/news/'
response = requests.get(yandex_url)
dom_ya = html.fromstring(response.text)
yandex_news = dom_ya.xpath('//article')

# source_ya = dom_ya.xpath('//span[@class="mg-card-source__time"]/..//a/@aria-label')
# name_news_ya = dom_ya.xpath('//div[@class="mg-card__annotation"]/text()')
# link_ya = dom_ya.xpath('//span[@class="mg-card-source__time"]/..//a/@href')
# date_ya_news = dom_ya.xpath('//span[@class="mg-card-source__time"]/text()')

ya_news_list = []

for ya_new in yandex_news:
    ya_news_dict = {}

    source_ya = ya_new.xpath('.//span[@class="mg-card-source__time"]/..//a/@aria-label')
    name_news_ya = ya_new.xpath('.//div[@class="mg-card__annotation"]/text()')
    link_ya = ya_new.xpath('.//span[@class="mg-card-source__time"]/..//a/@href')
    date_ya_news = ya_new.xpath('.//span[@class="mg-card-source__time"]/text()')


    ya_news_dict['_id'] = str(link_ya[0]) + str(name_news_ya[0])
    ya_news_dict['source'] = source_ya
    ya_news_dict['name_news_yandex'] = name_news_ya
    ya_news_dict['link_yandex'] = link_ya
    ya_news_dict['date_news_yandex'] = date_ya_news
    ya_news_list.append(ya_news_dict)
    add_mongo_collection(news_db, ya_news_dict)

pprint(ya_news_list)
