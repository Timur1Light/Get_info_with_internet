#1. Посмотреть документацию к API GitHub, разобраться как вывести список наименований
# репозиториев для конкретного пользователя, сохранить JSON-вывод в файле *.json.

#Импортируем библиотеки
import requests
import json

#Обозначаем переменные
url = 'https://api.github.com'
uname = input('Введите имя пользователя:')
uname = 'Timur1Light' if uname == '' else uname

#Получаем данные
r = requests.get(f'{url}/users/{uname}/repos')

#Сохраняем данные в файл
with open('D_Leason_1_1.json', 'w') as f:
    json.dump(r.json(), f)

#Выводим полученные данные
for i in r.json():
    print(i['name'])