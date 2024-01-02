import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import csv

url_main: str = "https://moba.ru/catalog/"


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


def find_data(url: str) -> None:
    option = webdriver.EdgeOptions()
    option.add_argument("--headless")
    driver = webdriver.Edge(options=option)
    driver.get(url)
    with open('table.csv', 'a') as table:
        while True:
            time.sleep(2)
            soup = BeautifulSoup(str(driver.page_source), 'lxml')
            blocks = soup.find_all('td', class_="wrapper_td")
            csvwriter = csv.writer(table)
            for i in blocks:
                name = i.find('a', class_='dark_link').text
                price = i.find('span', class_='price_value').text
                link = i.find('a', class_='dark_link')['href']
                csvwriter.writerow([name, price, 'https://moba.ru/'+link])
            try:
                driver.find_element(By.CLASS_NAME, 'flex-next').click()
            except:
                break
    driver.close()


def main():
    # get_page(url_main)
    # find_links()
    with open('links', 'r', encoding='utf-8') as file:
        links = list(map(lambda x: x[0:-2], file.readlines()))
    for i in range(0, len(links)):
        find_data(links[i])
        print(f"[+] Success complete page {i}")


if __name__ == "__main__":
    main()