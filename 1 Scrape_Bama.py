# to create database and scrape 100 page from bama.ir, only needs to run one time
# Scraping time depends on how many pages you want to scrape

import re
import string

import mysql.connector
import requests
from bs4 import BeautifulSoup

URL_TEMPLATE = 'https://bama.ir/car/all-brands/all-models/all-trims?hasprice=true&page=%d'
print('Please have patience...')
print('This process will take some time depending on\nthe number of pages and connection speed...')

db = mysql.connector.connect(user='root', password='PASSWORD', host='localhost')
cursor = db.cursor()


class Del:
    def __init__(self, keep=string.digits):
        self.comp = dict((ord(c), c) for c in keep)

    def __getitem__(self, k):
        return self.comp.get(k)


def initialize_db():
    cursor.execute("DROP DATABASE IF EXISTS bama")
    cursor.execute("CREATE DATABASE bama CHARACTER SET utf8 COLLATE utf8_persian_ci")
    cursor.execute("use bama")
    cursor.execute("DROP TABLE IF EXISTS info")
    cursor.execute(
        "CREATE TABLE info (ID INT PRIMARY KEY AUTO_INCREMENT, Model TINYTEXT, Brand TINYTEXT, Karkard INT, Year INT, Gheymat TINYTEXT) CHARACTER SET utf8 COLLATE utf8_persian_ci")


def extract_data_from_html(html_content):
    # This function will be cleaned up in the next commit!
    model = list()
    brand = list()
    gheymat = list()
    karkard = list()
    year = list()
    DD = Del()

    soup = BeautifulSoup(html_content.text, 'html.parser')
    all_karkard = soup.find_all('p', attrs={'class': 'price hidden-xs'})
    for kar in all_karkard:
        kar = re.sub('\s+', ' ', kar.text).strip()
        kar = kar.translate(DD)
        if kar == '':
            kar = 0
        karkard.append(int(kar))
    all_cars = soup.find_all('h2', attrs={'class': 'persianOrder'})
    for car in all_cars:
        car = re.sub('\s+', ' ', car.text).strip()
        car = car.split('،')
        car_model = car[0].strip()
        car_brand = car[1].strip()
        model.append(car_model)
        brand.append(car_brand)
    all_year = soup.find_all('span', attrs={'class': 'year-label visible-xs'})
    for years in all_year:
        years = re.sub('\s+', ' ', years.text).strip()
        years = years[:4]
        year.append(int(years))
    all_gheymat = soup.find_all('p', attrs={'class': 'cost'})
    for money in all_gheymat:
        money = re.sub('\s+', ' ', money.text).strip()
        money = money.translate(DD)
        if money == '':
            money = '-'
        gheymat.append(money)

    return zip(model, brand, karkard, year, gheymat)


def find_site(site):
    result = requests.get(site)
    for Model, Brand, Karkard, Year, Gheymat in extract_data_from_html(result):
        cursor.execute("INSERT INTO info (Model, Brand, Karkard, Year, Gheymat) VALUES (%s, %s, %s, %s, %s)", (
            Model, Brand, Karkard, Year, Gheymat
        ))
    db.commit()


def main():
    initialize_db()
    counter = 100
    while counter != 0:
        page = URL_TEMPLATE % counter
        find_site(page)
        counter -= 1
        print('Scraping Page %s' % (100 - counter))

    cursor.execute("DELETE FROM info WHERE Gheymat LIKE '-'")
    cursor.execute(
        "DELETE c1 FROM info c1 INNER JOIN info c2 WHERE c1.id > c2.id AND c1.Model = c2.Model AND c1.Brand = c2.Brand AND c1.Karkard = c2.Karkard AND c1.Year = c2.Year AND c1.Gheymat = c2.Gheymat")
    db.commit()
    print('Finished')
    print('Thank you for your patience')
    db.close()


if __name__ == '__main__':
    main()
