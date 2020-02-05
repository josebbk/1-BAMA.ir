# Used with csv
# To Predict Car Price With TreeClassifier

import os

import mysql.connector
import pandas as pd
from sklearn import tree
from sklearn.preprocessing import LabelEncoder

db = mysql.connector.connect(user='root', password='PASSWORD', host='localhost', database='bama')

model = input('Model: ')
brand = input('Brand: ')
karkard = int(input('Karkard: '))
year = int(input('Year: '))
cursor = db.cursor()

cursor.execute("SELECT * FROM info WHERE model=%s LIMIT 250", (model,))
result = cursor.fetchall()
csv = list()

for row in result:
    csv.append(row)

df = pd.DataFrame(csv)
df.to_csv('Predict.csv', index=None)
df = pd.read_csv('Predict.csv')
# remove csv
os.remove('Predict.csv')

inputs = df.drop(['0', '5'], axis='columns')
target = df['5']

new_row = pd.DataFrame({'1': model, '2': brand, '3': karkard, '4': year}, index=[0])
inputs = pd.concat([new_row, inputs]).reset_index(drop=True)

label = LabelEncoder()

inputs['Model'] = label.fit_transform(inputs['1'])
inputs['Brand'] = label.fit_transform(inputs['2'])
inputs['Karkard'] = label.fit_transform(inputs['3'])
inputs['Year'] = label.fit_transform(inputs['4'])

inputs_new = inputs.drop(['1', '2', '3', '4'], axis='columns')

# val_model = inputs_new.iloc[0]['Model']
val_brand = inputs_new.iloc[0]['Brand']
val_karkard = inputs_new.iloc[0]['Karkard']
val_year = inputs_new.iloc[0]['Year']

inputs_new.drop(inputs_new.index[0], inplace=True)

clf = tree.DecisionTreeClassifier()
clf = clf.fit(inputs_new, target)
answer = clf.predict([[0, val_brand, val_karkard, val_year]])
for a in answer:
    print('This Car Is Worth Around %s' % a)
