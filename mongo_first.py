import requests
from bs4 import BeautifulSoup as bs
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError as dke
from pprint import pprint

client = MongoClient('127.0.0.1', 27017)

db = client['vacancies_mongo']
vacancies_db = db.vacancies

searching = input('Введите параметры поиска: ')
number_of = int(input('Введите количество вакансий: '))

url = 'https://hh.ru'

params = {'fromSearchLine': 'true',
          'text': searching,
          'from': 'suggest_post',
          'search_field': 'description',
          'search_field': 'company_name',
          'search_field': 'name',
          'page': 0}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'}



def chec_money(money):
    if 'до' in money:
        money = money.replace('до', 'None')
    elif 'от ' in money:
        money = money.replace('от ', '')
        money = money.replace(' ', ' None ')
    elif money == 'None':
        money = 'None ' * 3
    else:
        money = money.replace('–', '')
    money = money.split()
    for i in range(0, 2):
        if money[i] != 'None':
            money[i] = int(money[i])
    return money

def add_mongo_collection(name_collection, name_doc):
    try:
        name_collection.insert_one(name_doc)
    except dke:
        print(f"такая вакансия с _id {name_doc['_id']} уже занесена в базу")



vacancy_list = []
end_count = 0
begin_count = db.vacancies.find().count()


while True:
    response = requests.get(url + '/search/vacancy', params=params, headers=headers)
    dom = bs(response.text, 'html.parser')
    vacancies = dom.find_all('div', {'class': 'vacancy-serp-item'})

    if response.ok and vacancies:

        for vacancy in vacancies:
            vacancy_data = {}
            link = vacancy.find('a', {'class': 'bloko-link'})['href']
            name_of_vacancy = vacancy.find('a', {'class': 'bloko-link'}).text
            if '\xa0' in name_of_vacancy:
                name_of_vacancy = name_of_vacancy.replace('\xa0', ' ')

            try:
                employer = vacancy.find('a', {'class': 'bloko-link bloko-link_secondary'}).text
                if '\xa0' in employer:
                    employer = employer.replace('\xa0', ' ')
            except:
                employer = 'None'
            location = vacancy.find_all('div', {'class': 'bloko-text bloko-text_small bloko-text_tertiary'})[1].text
            try:
                salary = vacancy.find_all('span', {'class': 'bloko-header-section-3 bloko-header-section-3_lite'})[1]
                salary = salary.text
                if '\u202f' in salary:
                    salary = salary.replace('\u202f', '', 2)
            except:
                salary = 'None'

            salary = chec_money(salary)

            vacancy_data['_id'] = employer + link + name_of_vacancy
            vacancy_data['link'] = link
            vacancy_data['name_of_vacancy'] = name_of_vacancy
            vacancy_data['employer'] = employer
            vacancy_data['location'] = location
            vacancy_data['url'] = url
            vacancy_data['salary'] = salary
            vacancy_list.append(vacancy_data)
            add_mongo_collection(vacancies_db, vacancy_data)



        print(f" Обработана {params['page'] + 1} страница")
        params['page'] += 1

    else:
        break
    if len(vacancy_list) >= number_of:
         break

# pprint(vacancy_list)
# print(len(vacancy_list))
if len(vacancy_list) == 0:
     print('Попробуйте ввести правильный параметр поиска')

end_count = db.vacancies.find().count()
print('Было добавлено', end_count - begin_count, 'новых записей')
