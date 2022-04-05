# Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы получаем должность)
# с сайтов HH(обязательно) и/или Superjob(по желанию). Приложение должно анализировать несколько страниц сайта
# (также вводим через input или аргументы). Получившийся список должен содержать в себе минимум:
# 1.Наименование вакансии.
# 2.Предлагаемую зарплату (разносим в три поля: минимальная и максимальная и валюта. цифры преобразуем к цифрам).
# 3.Ссылку на саму вакансию.
# 4.Сайт, откуда собрана вакансия.

from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint
import re
import time

base_url = 'https://hh.ru'
find_text = 'Data+since'
url = f'{base_url}/search/vacancy?area=113&fromSearchLine=true&text={find_text}&from=suggest_post&customDomain=1'
headers = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36'}

#делаем запрос
response = requests.get(url, headers=headers)

#сохраняем страницу в файл
#with open('response.html', 'w', encoding='utf-8') as f:
#    f.write(response.text)

# Читаем сохраненный файл
html_file = ''
with open('response.html', 'r', encoding='utf-8') as f:
    html_file = f.read()

#Создаем дом
dom = bs(html_file, 'html.parser')

#Ищем интересуещие элементы
jobs = dom.find_all('div', {'class':'vacancy-serp-item'})

#Создаем результирующий список
jobs_list = []

for job in jobs:
    job_data = {}
    #job_link = job.find('a', {'class': 'bloko-link'})['href']
    #Ищем нужный контейнер
    req = job.find('span', {'class': 'g-user-content'})
    #Если ответ получен то забираем данные
    if req != None:
        main_info = req.findChild()
        job_link = main_info['href']
        job_name = main_info.getText()
        payment = job.find('span', {'class': 'bloko-header-section-3'})
        # Если указанна сумма оплаты, обрабатываем ее, иначе записываем что ее нет.
        if payment:
            payment = re.sub(r'[–.]', "", payment.getText()).replace('\u202f', '').replace('до', '')
            payments = payment.split()
            payment_min = int(payments[0])
            #Если указанн диапазон, раскидываем его по соответсвующим переменным, иначе пишем что нет.
            if len(payments) > 2:
                payment_max = int(payments[1])
                payment_val = payments[2]
            else:
                payment_max = None
                payment_val = payments[1]

        else:
            payment_min = None
            payment_max = None
            payment_val = None

        #Сохраняем все полученные данные, делаем паузу и идем по циклу
        job_data['name'] = job_name
        job_data['payment_min'] = payment_min
        job_data['payment_max'] = payment_max
        job_data['valuta'] = payment_val
        job_data['link'] = job_link
        job_data['site'] = base_url
        jobs_list.append(job_data)
        time.sleep(1)
pprint(jobs_list)


