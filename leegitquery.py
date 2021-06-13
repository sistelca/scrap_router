import requests
import base64
import json
import hashlib

import mysql.connector
from dotenv import load_dotenv
import os


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
        try:
            return json.loads(jsonString)
        except:
            return jsonString 
 
    else:
        return 'Content was not found.'
    
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
        fl  = instrucions[asi][1]
        regq += z['op'] +' ' + y + ' ' + gna + z['set'] + fl + z['filtro']
        query.append(z['op'] +' ' + y + ' ' + gna.upper() + z['set'] + fl.upper() + z['filtro'])

    return regq, query


def conexion():
    load_dotenv()

    sql_id = os.getenv("SQL_ID")
    sql_pw = os.getenv("SQL_PW")
    cnx = mysql.connector.connect(user=sql_id, password=sql_pw, host='127.0.0.1', database='clientes')
    return cnx


def actualiza(querys):
    
    operation = ('; ').join(querys)
    
    try:
        
        cursor = cnx.cursor()
        result_iterator = cursor.execute(operation, multi=True)
        i = 0
        
        for res in result_iterator:
            print("Running query: ", res)
            print(f"Affected {res.rowcount} rows" )
            i += 1
            if i == len(querys): # evitar RuntimeError: 
                break # generator raised StopIteration
        cnx.commit()

        return True
    
    except:
        cnx.close()
        return "algo anda mal"

    
def consulta_existe(fireg):
    
    consulta = "SELECT COUNT(*) from Actzl WHERE firma = '{}'".format(fireg)
    
    cursor = cnx.cursor()
    cursor.execute(consulta)
    result=cursor.fetchone()
    number_of_rows=result[0]
    
    return number_of_rows > 0


def validacion(a, b):
    return a == hashlib.sha1(b.lower().encode('utf-8')).hexdigest()



path = '/home/luis/cibercom/desechosSolidos'
user = 'sistelca'
repo_name = 'desechosSolidos'
chek_orig = 'orig_data.sha1'
chek_dest = 'dest_data.sha1'

checkorg = leeactzl(user, repo_name, chek_orig)
checkdes = leeactzl(user, repo_name, chek_dest)


if checkorg != checkdes:

    # haciendo el git pull si hash difieren
    comando = "/bin/git -C {} pull origin master".format(path)
    os.system(comando)
    
    with open(os.path.join(path, "orig_data.json"), encoding = 'utf-8') as f:
        finalJson = json.load(f)

    cnx = conexion()

    for registro in finalJson:

        dt_query = json.loads(registro['instruccion'])
        fireg, querys = calcquerys(dt_query)

        if validacion(registro['firma'], fireg) and not consulta_existe(registro['firma']):

            # valor 0 en Actzl.pasar => query recibido no se sube a nube,
            # * en vez de ' inutiliza query descargado
            intru = registro['instruccion'].replace("'", "*")
            qact  = """INSERT INTO Actzl (reg_fecha, instruc, firma, pasar)"""
            qact += """ VALUES ('{}', '{}', '{}', 0)""".format(registro['fecha'], intru,
                                                               registro['firma'], 0)
            querys.append(qact)

            print(actualiza(querys))

        else:
            print(registro['firma'], "Existe ...")

    cnx.close()
    with open(os.path.join(path, chek_dest), 'w', encoding = 'utf-8') as f:
        f.write(checkorg)
    
    comandos = ["/bin/git -C {} add .", "/bin/git -C {} commit -m \"act\"", 
               "/bin/git -C {} push origin master"]
    
    for comando in comandos:
        tpcmd = comando.format(path)
        os.system(tpcmd)



