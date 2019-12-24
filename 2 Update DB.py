# To Update Database Daily

from bs4 import BeautifulSoup
import re
import requests
import string
import mysql.connector

class Del:
    def __init__(self, keep=string.digits):
        self.comp = dict((ord(c),c) for c in keep)
    def __getitem__(self, k):
        return self.comp.get(k)
DD = Del()


db = mysql.connector.connect(user='root', password='PASSWORD',
                            host='localhost', database='bama')
cursor = db.cursor()

model = list()
brand = list()
gheymat = list()
karkard = list()
year = list()

print('Updating DataBase...')

def find_site(site):
    del model[:]
    del brand[:]
    del gheymat[:]
    del karkard[:]
    del year[:]
    result = requests.get(site)
    soup = BeautifulSoup(result.text, 'html.parser')
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
    for Model, Brand, Karkard, Year, Gheymat in zip(model, brand, karkard, year, gheymat):
        cursor.execute("INSERT INTO info (Model, Brand, Karkard, Year, Gheymat) VALUES (%s, %s, %s, %s, %s)", (
            Model, Brand, Karkard, Year, Gheymat
            ))
    db.commit()


counter = 5
count_sec = 0
while counter != 0:
    page = 'https://bama.ir/car/all-brands/all-models/all-trims?hasprice=true&page='
    counter = str(counter)
    page = page + counter
    find_site(page)
    counter = int(counter) - 1
    count_sec += 1
    print('Updating, Page %s' % count_sec)

cursor.execute("DELETE FROM info WHERE Gheymat LIKE '-'")
cursor.execute("DELETE c1 FROM info c1 INNER JOIN info c2 WHERE c1.id > c2.id AND c1.Model = c2.Model AND c1.Brand = c2.Brand AND c1.Karkard = c2.Karkard AND c1.Year = c2.Year AND c1.Gheymat = c2.Gheymat")
db.commit()
db.close()

print('DataBase Updated.')