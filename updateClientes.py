# -*- coding: utf-8 -*-

import mysql.connector
from dotenv import load_dotenv
import os

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
        return list(cursor)
    

querys = ['update Actzl set pasar = 1 where pasar = 2',
          'select * from Actzl where pasar = 1',
          'update Actzl set pasar = 0 where pasar = 1']
    
for query in querys:
    ok = conexion(query)
    print(ok)
    

print("xd")
