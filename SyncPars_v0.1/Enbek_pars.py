import json
import lxml
import time
import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
from All_data_parser import all_city_data,all_prof_data
headers = {"Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0"}

def get_url_vac(headers):
    #Берем регионы
    city_keys = all_city_data.keys()
    ################################
    # Получаем ссылки на профессии во всех городах
    for city in city_keys:
        city_id = all_city_data[city]
        for prof in all_prof_data:
            for page in range(1, 100):
                url = f"https://www.enbek.kz/ru/search/vacancy?prof={prof}&except[subsidized]=subsidized&region_id={city_id}&page={page}"
                ###########################
                #Отправляю запрос на сайт
                try:
                    session = requests.session()
                    response = session.get(url=url,headers=headers)
                    #Создаю объект соупа для парсинга данных
                    soup = BeautifulSoup(response.text,'lxml')
                    ###########################################
                    #Проверка на наличие на странице вакансий
                    text = soup.find('div',class_="container mb-5").find('div',class_='row').find('div',class_='col-lg-8 col-xxl-9 position-relative content-search-vacancy').find('div',class_="text-center")
                    if str(text) == 'None':
                        #Ссылки на вакансию содержатся в классе item-list:
                        item_list = soup.find('div', class_="container mb-5").find('div', class_='row').find('div',class_='col-lg-8 col-xxl-9 position-relative content-search-vacancy').find_all('div', class_='item-list')
                        for item in item_list:
                            link = f"https://www.enbek.kz" + item.find('a',class_='stretched').get('href')
                            yield link,prof,city_id

                    else:
                        #На странице нету вакансий останавливаем цикл
                        # print("Страница пуста останавливаем цикл!")
                        break


                except Exception as ex :
                    print(ex)


def main():
    get_url_vac(headers=headers)
    i = 0
    data = {'Машинист': [], 'Менеджер': [], 'Аналитик': [], 'Дизайнер': [], 'Програмист': [], 'Оператор': [],
            'Мастер': []
        , 'Автомеханик': [], 'Администратор': [], 'Косметолог': [], 'Мастер декоративных работ': []
        , 'Метролог': [], 'Оптик-механик': [], 'Парикмахер': [], 'Строитель': [], 'Разнорабочий': [], 'Повар': [],
            'Кондитер': []
        , 'Сантехник': [], 'Сварщик': [], 'Слесарь': [], 'Специалист': [], 'Техник': []}
    for link,prof,city_id in get_url_vac(headers=headers):
        try:
            i += 1

            session = requests.session()
            response = session.get(link)
            #Начнем парсить все необходимые данные
            soup = BeautifulSoup(response.text,'lxml')
            #В контейнере содержится вся нужная инфа
            container = soup.find_all('div',class_='container')
            #Название профессии
            name = container[3].find('h4',class_='title')
            name = name.text
            #ЗП професии
            price = container[3].find('div',class_='price')
            price = price.text
            #Тип занятости професии
            type_work = container[3].find('ul',class_='info d-flex flex-column').find('li').find_all('span')
            type_work = type_work[1].text
            #Обязанности професии
            rslit = container[3].find_all('div',class_='single-line')[2].find('div',class_='value').text.replace("\n","").strip().split(';')
            for u in range(len(rslit)):
                rslit[u] = rslit[u].strip()
            #Дата публикации
            date = container[3].find('ul',class_='info small mb-2').find('li',class_='mb-0').text.strip()
            #Парсинг данных окончен
            #Сохраняем данные
            prof_dict = {'name' : name,'price' : price,'type_work' : type_work,'responsibilities' : rslit,'date' : date,'link_vac' : link,'prof' : prof,'city_id' : city_id}
            data[prof].append(prof_dict)

        except Exception as ex:
            print(ex)
        finally:
            with open('data{x}.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)



    # Создаем дамп всех данных
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

if __name__ == "__main__":
    main()
