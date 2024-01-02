import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import csv


url_main: str = "https://moba.ru/catalog/"
COUNT: int = 0


def get_page(url: str) -> None:
    option = webdriver.EdgeOptions()
    option.add_argument("--headless")
    driver = webdriver.Edge(options=option)
    driver.get(url)
    time.sleep(5)
    with open('text.txt', 'w', encoding='utf-8') as file:
        file.write(driver.page_source)
    driver.close()


def find_links() -> None:
    with open('text.txt', 'r', encoding='utf-8') as file:
        soup = file.read()
    soup = BeautifulSoup(soup, 'lxml')
    block = soup.find('ul', class_="left_menu").find_all('li')
    with open("links", "a+", encoding='utf-8') as file:
        for i in block:
            if str(i).count("menu_item") == 1 or str(i).count("child_container") == 0:
                print(i.find('a')['href'])
                file.write("https://moba.ru" + i.find('a')['href'] + '\n')


def find_articles_and_amount(url: str) -> list:
    option = webdriver.EdgeOptions()
    option.add_argument("--headless")

    driver = webdriver.Edge(options=option)
    driver.get(url)

    soup = BeautifulSoup(str(driver.page_source), 'lxml')

    article = soup.find('div', class_='article iblock').find('span', 'value').text
    name = soup.find('h1', id='pagetitle').text
    first_price = soup.find('div', class_='cost prices clearfix').find_all('span', class_='price_value')[0].text
    second_price = soup.find('div', class_='cost prices clearfix').find_all('span', class_='price_value')[1].text
    try:
        button = driver.find_element(By.CLASS_NAME, "right_info").find_element(By.CLASS_NAME, "buy_block").find_element(By.CLASS_NAME, "counter_wrapp").find_element(By.TAG_NAME, "input")
        button.clear()
        button.send_keys("51")
        button.click()
        amount = soup.find('span', class_="btn-lg w_icons to-cart btn btn-default transition_bg animate-load")[
            "data-quantity"]
        status = 'в наличии'
    except:
        amount = 0
        status = 'под заказ'
    print([name, article, first_price, second_price, amount, status])
    return [name, article, first_price, second_price, amount, status]


def find_data(url: str) -> None:

    global COUNT

    option = webdriver.EdgeOptions()
    option.add_argument("--headless")

    driver = webdriver.Edge(options=option)
    driver.get(url)

    with open('table.txt', 'a', encoding='utf-8') as table:

        while True:

            soup = BeautifulSoup(str(driver.page_source), 'lxml')
            blocks = soup.find_all('td', class_="wrapper_td")

            for i in blocks:
                link = i.find('a', class_='dark_link')['href']
                COUNT += 1
                table.write(f"https://moba.ru{link}\n")
            try:
                driver.find_element(By.CLASS_NAME, 'flex-next').click()
                print("okey")
            except:
                break
    driver.close()


def main():
    # get_page(url_main)
    # find_links()

    # with open('links', 'r', encoding='utf-8') as file:
    #    links = list(map(lambda x: x[0:-2], file.readlines()))
    # for i in range(0, len(links)):
    #
    #    find_data(links[i])
    #
    #    print(f"[+] Success complete page {i}")
    # print(f"Count : {COUNT}")
    second_main()


def second_main():
    with open('table.txt', 'r') as table:
        text = table.readlines()
    with open('table.csv', 'a', newline='') as table:
        csvrow = csv.writer(table)
        csvrow.writerow(['Название', 'Артикул', 'Первая Цена', 'Вторая Цена', 'Количество', 'В наличии'])
        for i in text:
            p = i.replace('\n', '').replace('//', '/').replace('/:', '//:')
            res = find_articles_and_amount(p)
            csvrow.writerow(res)
            print(f"[+] Success complete link {text.index(i)}/{len(text)}")


if __name__ == "__main__":
    main()
