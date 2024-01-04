import time
import csv
import sched
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
from multiprocessing import Pool


# URL для сбора ссылок на категории товаров
url_1: str = "https://omsk.moba.ru/catalog/akkumulyatory-1/filter/imyie_stores4filter-is-omsk/apply/"
url_2: str = "https://omsk.moba.ru/catalog/korpusa-zadnie-kryshki/filter/imyie_stores4filter-is-omsk/apply/"
url_3: str = "https://omsk.moba.ru/catalog/shleyfy-platy/filter/imyie_stores4filter-is-omsk/apply/"
url_4: str = "https://omsk.moba.ru/catalog/displei/filter/imyie_stores4filter-is-omsk/apply/"
# Функция для сохранение страницы с каталогами
urls: tuple = (url_1, url_2, url_3, url_4)

# Сбор ссылок на каталоги
def find_links() -> None:
    # Открываем файл с содержанием страницы от каталогов
    with open('text.txt', 'r', encoding='utf-8') as file:
        soup = file.read()
    # Создаём объект "Супа"
    soup = BeautifulSoup(soup, 'lxml')
    # Сбор ссылок на каталоги
    block = soup.find('ul', class_="left_menu").find_all('li')
    # Запись в файл links ссылок на каталоги
    with open("links", "a+", encoding='utf-8') as file:
        # Проход по каталогам
        for i in block:
            # Проверка ссылки на "ссылку ребёнка"
            if str(i).count("menu_item") == 1 or str(i).count("child_container") == 0:
                # Записываем ссылку в файл
                file.write("https://omsk.moba.ru" + i.find('a')['href'] + '\n')


# Сбор информации о товаре
def find_articles_and_amount(url: str) -> None:

    # Опции для без экранного захода на сайт
    option = webdriver.ChromeOptions()
    #option.add_argument("--window-size=10,10")
    option.add_argument('--headless')



    # Посылаем GET запрос на сайт
    driver = webdriver.Chrome(options=option)
    driver.get(f'{url}?cid=14411')
    #time.sleep(2)
    # Создаём объект "Супа"
    soup = BeautifulSoup(str(driver.page_source), 'lxml')
    # "Отлов" ошибок при сборе информации о товаре
    try:

        button = driver.find_element(By.ID, f'bx_117848907_{url.split("/")[-2]}_quantity')
        button.click()
        button.send_keys("51")
        button.click()
        button.send_keys(Keys.ENTER)
        #time.sleep(2)
        amount = driver.find_element(By.ID, f"bx_117848907_{url.split('/')[-2]}_basket_actions").find_element(By.TAG_NAME, "span")

        amount = str(amount.get_attribute("data-quantity"))
        # Сбор артикула
        article = soup.find('div', class_='article iblock').find('span', class_='value').text
        # Сбор названия
        name = soup.find('h1', id='pagetitle').text.replace(',', ' ')
        # Сбор первой цены
        first_price = soup.find('div', class_='cost prices clearfix').find_all('span', class_='price_value')[0].text
        # Сбор второй цены
        second_price = soup.find('div', class_='cost prices clearfix').find_all('span', class_='price_value')[1].text
    except:
        # При ошибке сбора информации переходим к следующей ссылке
        return
    # "Отлов" ошибки при сборе информации о наличии товара
    try:
        # Сбор информации о наличии товара
        status = soup.find('div', class_='quantity_block_wrapper').find('span', class_='item_instock value').text
    except:
        # При ошибке, нет в наличии
        status = 'Под заказ'

    # Открываем csv файл для добавлении информации о товаре
    with open('table.csv', 'a', newline='') as table:
        csvrow = csv.writer(table)
        # Записываем информацию о товаре в строку
        csvrow.writerow([name, article, first_price, second_price, amount, status])


# Сбор ссылок на товары
def find_data(url: str) -> None:

    # Опции для без экранного захода на сайт
    option = webdriver.EdgeOptions()
    option.add_argument("--headless")

    # Посылаем GET запрос на сайт
    driver = webdriver.Edge(options=option)
    driver.get(url)

    # Открываем файл для записи в него ссылок на товары

    with open('table.txt', 'a+', encoding='utf-8') as table:

        # Создаём объект "Супа"

        soup = BeautifulSoup(str(driver.page_source), 'lxml')

        # Поиск "блоков" с ссылкой на товар

        blocks = soup.find_all('td', class_="wrapper_td")

        for i in blocks:

            # Поиск ссылки на товар

            link = i.find('a', class_='dark_link')['href']

            # Подготовляем ссылку

            word = f"https://omsk.moba.ru{link}\n"

            # Запись ссылки в файл

            table.write(word)

        # Закрываем "запрос"

        driver.close()


# Поиск количества страниц в каталоге на товар
def pagination_find(link: str):

    # Опции для без экранного захода на сайт
    option = webdriver.EdgeOptions()
    option.add_argument("--headless")

    # Посылаем GET запрос на сайт
    driver = webdriver.Edge(options=option)
    driver.get(link)

    # Создаём объект "Супа"
    soup = BeautifulSoup(str(driver.page_source), 'lxml')

    # Проверка: имеются ли вообще страницы в каталоге
    try:
        # Путь к "пагинации"
        page = int(soup.find_all('a', class_='dark_link')[-1].text)
    except:
        return 0
    links: list = []
    # Проход по страницам
    for i in range(1, page + 1):
        # Кидаем ссылку на сбор с неё информацию
        links.append(f'{link}?PAGEN_1={i}')

    pool2 = Pool(5)
    pool2.map(find_data, links)


# Запуск первой части программы
def first_main():
    # get_page(url_main) - сохранение страницы с каталогами
    # find_links() - извлечение ссылок из каталогов

    # Создаём "бассейн" процессов их количество равно 10 можно поставить сколько вам угодно
    pool = Pool(10)

    # Записываем в список links ссылки на каталоги
    with open('links', 'r', encoding='utf-8') as file:
        # Преобразуем данные из файла в список ссылок
        links = list(map(lambda x: x[0:-2], file.readlines()))

    # Многопоточная работа с ссылками
    pool.map(pagination_find, links)

    # Обработка последней ссылки
    pagination_find(links[-1])


# Запуск второй части программы
def second_main():

    # Извлекаем ссылки из файла
    with open('table.txt', 'r') as table:
        text = table.readlines()

    # Запись "шапки" в таблицу
    with open('table.csv', 'a', newline='') as table:
        csvrow = csv.writer(table)
        # "Шапка" таблицы
        csvrow.writerow(['Название', 'Артикул', 'Первая Цена', 'Вторая Цена', 'Количество','В наличии'])

    # Список ссылок
    result: list = []

    # Заполняем список ссылками
    for i in text:
        # Подготавливаем ссылку
        p = i.replace('\n', '')
        # Добавляем ссылку
        result.append(p)

    # Создаём "бассейн" процессов их количество равно 10 можно поставить сколько вам угодно
    pool = Pool(10)
    # Многопоточная работа с ссылками
    pool.map(find_articles_and_amount, result)



# Запуск всей программы (Точка входа)
def main():
    # Сбор ссылок на товары и запись их в файл
    #first_main()
    # Сбор информации о товаре и запись их в таблицу
    #second_main()

    #for i in urls:
    #    pagination_find(i)

    second_main()


# Запуск скрипта
if __name__ == "__main__":
    main()
