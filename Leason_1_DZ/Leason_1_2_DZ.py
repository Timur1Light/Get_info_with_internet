#2. Изучить список открытых API (https://www.programmableweb.com/category/all/apis).
# Найти среди них любое, требующее авторизацию (любого типа).
# Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.
import requests
import json

#Обозначаем переменные
url = 'https://api.vk.com'
metod = 'groups.get'
token = '84bb6670a78b468d9f4d9a721030f7fc24d49067d8b0a77a28089c166c36afddc0aff0512b01620f55a6a'

#Получаем данные
r = requests.get(f'{url}/method/{metod}?v=5.81&access_token={token}')

#Сохраняем данные в файл
with open('D_Leason_1_2.json', 'w') as f:
    json.dump(r.json(), f)

#print(r.text)
#Выводим полученные данные
print(r.json())
