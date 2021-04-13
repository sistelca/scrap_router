# -*- coding: utf-8 -*-

import mysql.connector
from dotenv import load_dotenv
import os
import datetime
import json

load_dotenv()

sql_id = os.getenv("SQL_ID")
sql_pw = os.getenv("SQL_PW")


def conexion(query):
    try:
        cnx = mysql.connector.connect(user=sql_id, password=sql_pw, host='127.0.0.1', database='clientes')
        cursor = cnx.cursor()
        seleccion = (query)
        cursor.execute(seleccion)
        cnx.commit()
        return 'ok'
    except:
        cnx = mysql.connector.connect(user=sql_id, password=sql_pw, host='127.0.0.1', database='clientes')
        cursor = cnx.cursor()
        seleccion = (query)
        cursor.execute(seleccion)
        return (list(cursor), cursor.description)
    

querys = ['update Actzl set pasar = 1 where pasar = 2',
          'select * from Actzl where pasar = 1',
          'update Actzl set pasar = 0 where pasar = 1']

claves = ''
    
okis = []
for query in querys:
    okis.append(conexion(query))
    
field_names = [i[0] for i in okis[1][1]]

print(field_names)

pila = []
for ok in okis[1][0]:
    uni = {}
    for l, v in zip(field_names[:-1], ok[:-1]):
        if isinstance(v, datetime.datetime):
            uni[l] = str(v)
        else:
            uni[l] = v
    pila.append(uni)
    #break

with open('result.json', 'w') as fp:
    json.dump(pila, fp)
print('listo')