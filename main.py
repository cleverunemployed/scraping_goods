import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import csv
import asyncio


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
                file.write("https://moba.ru/" + i.find('a')['href'] + '\n')


async def find_data(url: str) -> None:

    global COUNT

    option = webdriver.EdgeOptions()
    option.add_argument("--headless")

    driver = webdriver.Edge(options=option)
    driver.get(url)

    with open('table.csv', 'a', newline='') as table:

        csvwriter = csv.writer(table)

        while True:

            time.sleep(2)

            soup = BeautifulSoup(str(driver.page_source), 'lxml')
            blocks = soup.find_all('td', class_="wrapper_td")

            for i in blocks:
                name = i.find('a', class_='dark_link').text
                price_first = i.find_all('span', class_='price_value')[0].text
                price_second = i.find_all('span', class_='price_value')[1].text
                link = i.find('a', class_='dark_link')['href']
                COUNT += 1
                csvwriter.writerow([name, price_first, price_second, 'https://moba.ru/'+link])
            try:
                driver.find_element(By.CLASS_NAME, 'flex-next').click()
            except:
                break
    driver.close()


async def main():
    # get_page(url_main)
    # find_links()
    with open('table.csv', 'a') as table:
        csvwriter = csv.writer(table)
        csvwriter.writerow(["Наименование", "Первая цена", "Вторая цена", "Ссылка"])
    with open('links', 'r', encoding='utf-8') as file:
        links = list(map(lambda x: x[0:-2], file.readlines()))
    for i in range(0, len(links)):

        await find_data(links[i])
        await asyncio.sleep(2)

        print(f"[+] Success complete page {i}")
    print(f"Count : {COUNT}")

if __name__ == "__main__":
    asyncio.run(main())