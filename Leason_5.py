from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from pymongo import MongoClient
from time import sleep



client = MongoClient('127.0.0.1', 27017)
db = client['mail']
mail_collections = db.mail.ru

options = Options()
options.add_argument("start-maximized")

serv = Service('./chromedriver')
driver = webdriver.Chrome(service=serv, options=options)

wait = WebDriverWait(driver, 15)



def write_data_id(write_data):
    if mail_collections.find_one({'_id': write_data['_id']}):
        print(f'Запись уже существует. ID:  {write_data["_id"]}')
    else:
        mail_collections.insert_one(write_data)
        print(f'Запись успешна завершена. ID: {write_data["_id"]}')



def mail_autorisation():
    driver.get('https://account.mail.ru/login')

    elem = wait.until(EC.presence_of_element_located((By.NAME, 'username')))
    elem.send_keys("study.ai_172@mail.ru")
    elem.send_keys(Keys.ENTER)

    elem = wait.until(EC.presence_of_element_located((By.NAME, 'password')))
    sleep(1)
    elem.send_keys("NextPassword172#")
    elem.send_keys(Keys.ENTER)



def get_mail_link():
    links = []
    xpath = "//a[contains(@href,'/inbox/0:')]"
    wait.until(EC.presence_of_element_located((By.XPATH, xpath)))

    last_id = None
    while True:
        letters = driver.find_elements(By.XPATH, xpath)
        end_id = letters[-1].get_attribute('href')
        if last_id == end_id:
            break

        for letter in letters:
            links.append(letter.get_attribute('href').split('?')[0])

        last_id = end_id
        actions = ActionChains(driver)
        actions.move_to_element(letters[-1]).perform()
        sleep(2)
    links = list(set(links))

    return links



def get_mail_data(links):
    for link in links:
        driver.get(link)
        wait.until(EC.presence_of_element_located((By.XPATH,
                                                       "//h2[@class='thread-subject']")))
        sleep(1)
        h2 = wait.until(EC.presence_of_element_located((By.XPATH, "//h2[@class='thread-subject']"))).get_attribute(
            "innerText")
        frm = wait.until(EC.presence_of_element_located((By.XPATH, "//span[@class='letter-contact']"))).get_attribute(
            "title")
        date = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='letter__date']"))).get_attribute(
            "innerText")
        text = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='letter__body']"))).get_attribute(
            "innerText")

        el = {}
        el['from'] = frm
        el['date'] = date
        el['topic'] = h2
        el['text'] = text.replace('\n', ' ').replace('\t', ' ')
        el['_id'] = link[link.find('inbox/0:') + 8:link.find(':0/')]

        write_data_id(el)

############################################################

mail_autorisation()
get_mail_data(get_mail_link())

