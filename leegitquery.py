import requests
import json
import hashlib

import mysql.connector
from dotenv import load_dotenv
import os


def calcquerys(dt_query):

    instrucions =  {'update': ['set', 'where'],
                 'insert into': ['(', ') values'],
                 'delete from': ['where', 'todo']
               }

    regq = ''
    query = []

    for y in dt_query.keys():
        z = dt_query[y]
        asi = z['op'].lower()
        gna = instrucions[asi][0]
        if instrucions[asi][1] != 'todo':
            fl = instrucions[asi][1]
        else:
            fl = ''

        regq += z['op'] +' ' + y + ' ' + gna + z['set'] + fl + z['filtro']
        query.append(z['op'] +' ' + y + ' ' + gna.upper() + z['set'] + fl.upper() + z['filtro'])
        
    retregq = hashlib.sha1(regq.lower().encode('utf-8')).hexdigest()

    return retregq, query


def conexion():
    load_dotenv()

    sql_id = os.getenv("SQL_ID")
    sql_pw = os.getenv("SQL_PW")
    cnx = mysql.connector.connect(user=sql_id, password=sql_pw, host='127.0.0.1', database='clientes')
    return cnx


def actualiza(petts):

    operation = ('; ').join(petts)

    try:
        cursor = cnx.cursor()
        if len(petts) > 1:
            
            result_iterator = cursor.execute(operation, multi=True)
            #i = 0

            for res in result_iterator:
                print("Running query: ", res)
                print(f"Affected {res.rowcount} rows" )
                #i += 1
                #if i == len(petts): # evitar RuntimeError:
                #    break # generator raised StopIteration

        else:

            cursor.execute(operation)
        cnx.commit()

        return True

    except:
        cnx.close()
        return operation


def consulta_existe(fireg):

    consulta = """SELECT COUNT(*) from Actzl WHERE firma = '{}'""".format(fireg)
    cnx = conexion()
    cursor = cnx.cursor()
    cursor.execute(consulta)
    result=cursor.fetchone()
    number_of_rows=result[0]
    cnx.close()
    return number_of_rows > 0


def giter(cmd, path):
    if cmd == "pull":
        comandos = ["/bin/git -C {} pull origin master"]
    elif cmd == "push":
        comandos = ["/bin/git -C {} add .", "/bin/git -C {} commit -m \"act\"",
                    "/bin/git -C {} push origin master"]

    for comando in comandos:
        tpcmd = comando.format(path)
        os.system(tpcmd)
    return True

def leeshas(file):
    try:
        with open(file, encoding = 'utf-8') as f:
            return f.readline()
    except:
        return 'vacio'

path = '/home/luis/cibercom/desechosSolidos'
chek_orig = 'orig_data.sha1'
chek_dest = 'dest_data.sha1'

giter("pull", path)


checkorg = leeshas(os.path.join(path, chek_orig))
checkdes = leeshas(os.path.join(path, chek_dest))


if checkorg != checkdes and checkorg != 'vacio':

    with open(os.path.join(path, "orig_data.json"), encoding = 'utf-8') as f:
        finalJson = json.load(f)

    cnx = conexion()

    for registro in finalJson:
        datax = registro['instruccion']
        dt_query = json.loads(datax.replace('u00', '\\u00'))
        fireg, querys = calcquerys(dt_query)

        if registro['firma'] == fireg and not consulta_existe(registro['firma']):

            # valor 0 en Actzl.pasar => query recibido no se sube a nube,
            # * en vez de ' inutiliza query descargado
            intru = registro['instruccion'].replace("'", "*")
            qact  = """INSERT INTO Actzl (reg_fecha, instruc, firma, pasar)"""
            qact += """ VALUES ('{}', '{}', '{}', 0)""".format(registro['fecha'], intru,
                                                               registro['firma'], 0)
            querys.append(qact)

            print(actualiza(querys))

        elif consulta_existe(registro['firma']):
            query = """UPDATE Actzl set pasar=0 WHERE firma='{}'""".format(fireg)
            print(actualiza([query]), '\n')

    cnx.close()
    with open(os.path.join(path, chek_dest), 'w', encoding = 'utf-8') as f:
        f.write(checkorg)

    giter("push", path)
    os.system("/home/luis/cibercom/actlz.sh")
