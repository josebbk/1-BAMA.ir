# To Update Database Daily

import string

import mysql.connector
import requests
from bs4 import BeautifulSoup

URL_TEMPLATE = 'https://bama.ir/car/all-brands/all-models/all-trims?hasprice=true&page=%d'

db = mysql.connector.connect(user='root', password='PASSWORD', host='localhost', database='bama')
cursor = db.cursor()

print('Updating DataBase...')


def validate_number(bama_string: str):
    a = "".join(i if i in string.digits else "" for i in bama_string)
    if a:
        return int(a)
    else:
        return None


def extract_data_from_html(html_content):
    soup = BeautifulSoup(html_content.text, 'html.parser')
    main_section = soup.find("div", {"class": "eventlist car-ad-list-new clearfix"})
    for section in main_section.find_all("li"):
        title = section.find_all('h2', attrs={'itemprop': 'name'})[-1].text
        car_model = title.split("،")[0]
        car_brand = title.split("،")[1]
        karkard = validate_number(section.find('p', attrs={'class': 'price hidden-xs'}).text)
        year = validate_number(section.find('span', attrs={'class': 'year-label visible-xs'}).text)
        price = validate_number(section.find("span", {"itemprop": "cost"}).text)
        yield car_model, car_brand, karkard, year, price


def find_site(site):
    result = requests.get(site)
    for Model, Brand, Karkard, Year, Gheymat in extract_data_from_html(result):
        cursor.execute("INSERT INTO info (Model, Brand, Karkard, Year, Gheymat) VALUES (%s, %s, %s, %s, %s)", (
            Model, Brand, Karkard, Year, Gheymat
        ))
    db.commit()


def main():
    counter = 5
    while counter != 0:
        page = URL_TEMPLATE % counter
        find_site(page)
        counter -= 1
        print('Scraping Page %s' % (5 - counter))

    cursor.execute("DELETE FROM info WHERE Gheymat LIKE '-'")
    cursor.execute(
        "DELETE c1 FROM info c1 INNER JOIN info c2 WHERE c1.id > c2.id AND c1.Model = c2.Model AND c1.Brand = c2.Brand AND c1.Karkard = c2.Karkard AND c1.Year = c2.Year AND c1.Gheymat = c2.Gheymat")
    db.commit()
    db.close()

    print('DataBase Updated.')


if __name__ == '__main__':
    main()
