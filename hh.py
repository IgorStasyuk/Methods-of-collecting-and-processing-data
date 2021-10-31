import requests
from bs4 import BeautifulSoup as bs
from pprint import pprint

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

vacancy_list = []
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
                money = vacancy.find_all('span', {'class': 'bloko-header-section-3 bloko-header-section-3_lite'})[1]
                money = money.text
                if '\u202f' in money:
                    money = money.replace('\u202f', '', 2)
            except:
                money = 'None'

            if 'до' in money:
                money = money.replace('до', 'None')
            elif 'от ' in money:
                money = money.replace('от ', '')
                money = money.replace(' ', ' None ')
            elif money == 'None':
                money = 'None ' * 3
            else:
                money = money.replace('–', '')

            vacancy_data['link'] = link
            vacancy_data['name_of_vacancy'] = name_of_vacancy
            vacancy_data['employer'] = employer
            vacancy_data['location'] = location
            vacancy_data['url'] = url
            vacancy_data['money'] = money
            vacancy_list.append(vacancy_data)

        print(f" Обработана {params['page'] + 1} страница")
        params['page'] += 1

    else:
        break
    if len(vacancy_list) >= number_of:
         break

pprint(vacancy_list)
print(len(vacancy_list))
if len(vacancy_list) == 0:
    print('Попробуйте ввести правильный параметр поиска')
