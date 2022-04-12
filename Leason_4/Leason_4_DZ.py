from lxml import html
from pymongo import MongoClient
import requests
from datetime import datetime
from pprint import pprint
import re

url_lenta = 'https://lenta.ru'
url_mail = 'https://news.mail.ru/'
url_ya = 'https://yandex.ru/news'

########################################################
def write_data_id(write_data):
    client = MongoClient('127.0.0.1', 27017)
    db = client['news']
    if 'news.mail.ru' in write_data['link']:
        news_collections = db.news_mail
    if 'https://yandex.ru/news' in write_data['link']:
        news_collections = db.news_ya  # news_mail #news_lenta

    if news_collections.find_one({'_id': write_data['_id']}):
        print(f'Запись уже существует. ID:  {write_data["_id"]}')
    else:
        news_collections.insert_one(write_data)
        print(f'Запись успешна завершена. ID: {write_data["_id"]}')


def write_data(write_data):
    client = MongoClient('127.0.0.1', 27017)
    db = client['news']
    news_collections = db.news_lenta #news_lenta
    if news_collections.find_one({'link': write_data['link']}):
        print(f'Запись уже существует. link:  {write_data["link"]}')
    else:
        news_collections.insert_one(write_data)
        print(f'Запись успешна завершена. link: {write_data["link"]}')


def get_dom(url):
    headers = {
        'User-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        dom = html.fromstring(response.text)
        return dom
    else:
        print(f'Запрос к адресу {response.url} завершился ошибкой: {response.status_code}.  '
              f'Текст ошибки: {response.text}')
        #return response


def get_date(time):
    if len(time) ==5:
        time = str(datetime.today().strftime('%Y-%m-%d')) +" " + time
    return time


def get_lenta_news(dom):
    top_news = dom.xpath('//div[@class="topnews__first-topic"]')[0]
    news_list = []
    all_news = dom.xpath("//a[@class='card-mini _topnews']")
    all_news.append(top_news)
    for news in all_news:
        news_data = {}
        if news.xpath(".//a/@class"):
            link = top_news.xpath(".//a/@href")[0]
            title = top_news.xpath(".//h3/text()")[0]
            time = top_news.xpath(".//time[@class='card-big__date']/text()")[0]
        else:
            link = news.xpath(".//@href")[0]
            title = news.xpath(".//span[@class='card-mini__title']/text()")[0]
            time = news.xpath(".//time[@class='card-mini__date']/text()")[0]
        if link[0] == '/':
            link = url_lenta + link
        time = get_date(time)
        news_data['link'] = link
        news_data['title'] = title
        news_data['time'] = time
        news_data['resourse'] = url_lenta
        news_list.append(news_data)
        write_data(news_data)
    pprint(news_list)


def get_mail_news(dom):
    main = dom.xpath('//div[@data-logger="news__MainTopNews"]')[0]
    links = main.xpath(".//td[@class='daynews__item']//a/@href")
    links.extend(main.xpath(".//td[@class='daynews__main']//a/@href"))
    links.extend(main.xpath(".//li[@class='list__item']//a/@href"))
    news_list = []
    for link in links:
        news_data = {}
        dom = get_dom(link)
        resource = dom.xpath("//a[contains(@class, 'breadcrumbs__link')]/span/text()")[0]
        title = dom.xpath("//h1[@class='hdr__inner']/text()")[0]
        time = dom.xpath("//span[@class='breadcrumbs__item']//span[@datetime]/@datetime")[0].replace('T', ' ')[:16]
        news_data['link'] = link
        news_data['title'] = title
        news_data['time'] = time
        news_data['resource'] = resource
        news_data['_id'] = "".join(re.findall(r'\d+', link))
        news_list.append(news_data)
        write_data_id(news_data)
    pprint(news_list)


def get_ya_news(dom):
    main = dom.xpath("//div[contains(@class, 'news-top-flexible-stories')]/div")
    news_list = []
    for news in main:
        news_data = {}
        links = news.xpath(".//a")
        title = links[0].xpath("./text()")[0].replace('\xa0', ' ')
        link = links[0].xpath("./@href")[0]
        time = news.xpath(".//span/text()")[0]
        time = get_date(time)
        recource = links[1].xpath("./text()")[0]
        news_data['link'] = link
        news_data['title'] = title
        news_data['time'] = time
        news_data['resource'] = recource
        news_data['_id'] = news_data['link'][news_data['link'].find('_id=')+4:news_data['link'].find('&story')]
        news_list.append(news_data)
        write_data_id(news_data)
    pprint(news_list)

####################################################

get_lenta_news(get_dom(url_lenta))
get_mail_news(get_dom(url_mail))
get_ya_news(get_dom(url_ya))
