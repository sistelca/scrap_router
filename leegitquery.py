# coding: utf-8


import requests
import base64
import json
import re
import hashlib

import mysql.connector
from dotenv import load_dotenv
import os


def campos(fields):
    cad = ''
    for x in fields.keys():
        cad += x + ' = ' + fields[x] + ', '
    return cad[:-2]

def leeactzl(user, repo_name, path_to_file):
    json_url ='https://api.github.com/repos/{}/{}/contents/{}'.format(user, repo_name,
                                                                      path_to_file)
    response = requests.get(json_url) #get data from json file located at specified URL 

    if response.status_code == requests.codes.ok:
        jsonResponse = response.json()  # the response is a JSON
        #the JSON is encoded in base 64, hence decode it
        content = base64.b64decode(jsonResponse['content'])
        #convert the byte stream to string
        jsonString = content.decode('utf-8')
        return json.loads(jsonString)
 
    else:
        return 'Content was not found.'
    
def calcquerys(finalJson):
    
    querys = []
    for registro in finalJson:
        if registro['firma'] == hashlib.sha1(registro["instruccion"].encode('utf-8')).hexdigest():
            dt_query = json.loads(registro['instruccion'])
            
            quetmp = []
            for y in dt_query.keys():
                if dt_query[y]['op'] == 'UPDATE':
                    query  = str(dt_query[y]['op']) + ' ' + y + ' SET ' + campos(dt_query[y]['fields'])
                    query += ' WHERE '
                elif dt_query[y]['op'] == 'INSERT INTO':
                    query  = query = str(dt_query[y]['op']) + ' ' + y
                    query += ' ' + str(tuple(list(dt_query[y]['fields'].keys())))+ ' VALUES '
                    query +=  str(tuple(list(dt_query[y]['fields'].values())))
                    query  = query.replace("'", "")
                    filtro_update = 'coduser = ' + dt_query[y]['fields']['coduser']
                quetmp.append(query)
                
            quetmp = [q + filtro_update if 'UPDATE' in q else q for q in quetmp]

            querys.extend(quetmp)

            #break # <--== Pilas quitar en produccion

    
    patron = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}')

    for i, query in enumerate(querys):
        for r in patron.findall(querys[i]):
            querys[i] = querys[i].replace(r, "'" + r + "'")

    return querys

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


user = 'sistelca'
repo_name = 'desechosSolidos'
path_to_file = 'data_actzl.json'

finalJson = leeactzl(user, repo_name, path_to_file)



# Ojo hay que registrar el hash en db receptora para vefiricar que no este y ejecutar 
# query

load_dotenv()

sql_id = os.getenv("SQL_ID")
sql_pw = os.getenv("SQL_PW")

bischo = calcquerys(finalJson)


for bis in bischo:
# pendiente por probar
     #ok = conexion(bis)
     #print(bis + ok)
     print(bis)



