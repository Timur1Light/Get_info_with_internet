from pymongo import MongoClient
from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint
import re
import time

client = MongoClient('127.0.0.1', 27017)
db = client['hh_db']
hh_collections = db.hh_col

base_url = 'https://hh.ru'
find_text = 'python'
page_limit = 1
jobs_list = []


def find_salary(num):
    r = {'$or': [{'salary_max': {'$gte': num}},
                   {'salary_min': {'$gte': num}}]}
    try:
        return hh_collections.find(r)
    except Exception as e:
        print('Ошибка при данных из базы:')
        print(e)
        return []


def write_data(job_data):
    if hh_collections.find_one({'id': job_data['id']}):
        print(f'Запись уже существует. ID:  {job_data["id"]}')
    else:
        hh_collections.insert_one(job_data)
        print(f'Запись успешна завершена. ID: {job_data["id"]}')


############
def get_num_page(dom)-> int:
    try:
        return int(dom.select('.pager a span')[-2].getText())
    except:
        return 1

############
def get_response(url):
    headers = {
        'User-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response
    else:
        print(f'Запрос к адресу {response.url} завершился ошибкой: {response.status_code}.  '
              f'Текст ошибки: {response.text}')
        return response

##################
def get_salarys(salary):
    salarys_data = {'salary_min': None, 'salary_max': None, 'salary_val': None}
    if salary:
        salarys = re.sub(r'[–.]', "", salary.getText()).replace('\u202f', '').split()
        if 'от' in salarys:
            salarys_data['salary_min'] = int(salarys[1])
            salarys_data['salary_val'] = salarys[2]
        if 'до' in salarys:
            salarys_data['salary_max'] = int(salarys[1])
            salarys_data['salary_val'] = salarys[2]
        if 'от' not in salarys and 'до' not in salarys:
            salarys_data['salary_min'] = int(salarys[0])
            salarys_data['salary_max'] = int(salarys[1])
            salarys_data['salary_val'] = salarys[2]
    return salarys_data

url = f'{base_url}/search/vacancy?clusters=true&area=113&no_magic=true&ored_clusters=true&items_on_page=' \
      f'20&enable_snippets=true&salary=&text={find_text}&page=0&hhtmFrom=vacancy_search_list'

response = get_response(url)
dom_pl = bs(response.text, 'html.parser')
page_limit = get_num_page(dom_pl)

for page in range(page_limit):
    url = f'{base_url}/search/vacancy?clusters=true&area=113&no_magic=true&ored_clusters=true&items_on_page=' \
          f'20&enable_snippets=true&salary=&text={find_text}&page={page}&hhtmFrom=vacancy_search_list'
    response = get_response(url)
    dom = bs(response.text, 'html.parser')
    jobs = dom.find_all('div', {'class': 'vacancy-serp-item'})

    for job in jobs:
        job_data = {}
        # Ищем нужный контейнер
        req = job.find('span', {'class': 'g-user-content'})
        # Если ответ получен то забираем данные
        if req != None:
            main_info = req.findChild()
            job_link = main_info['href']
            job_name = main_info.getText()
            salary = job.find('span', {'class': 'bloko-header-section-3'})
            salarys_data = get_salarys(salary)

            job_data['name'] = job_name
            job_data['salary_min'] = salarys_data['salary_min']
            job_data['salary_max'] =  salarys_data['salary_max']
            job_data['salary_val'] = salarys_data['salary_val']
            job_data['link'] = job_link
            job_data['site'] = base_url
            job_data['id'] = job_link[job_link.find('vacancy/')+8:job_link.find('?from')]
            write_data(job_data)
            jobs_list.append(job_data)
            time.sleep(1)

    pprint(jobs_list)

for doc in find_salary(100000):
    pprint(doc)




