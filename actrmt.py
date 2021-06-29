import mysql.connector
from dotenv import load_dotenv
import os
import json
import hashlib
import requests

def conexion():
    load_dotenv()

    sql_id = os.getenv("SQL_ID")
    sql_pw = os.getenv("SQL_PW")
    #sql_hs = os.getenv("SQL_HOST")
    sql_db = os.getenv("SQL_DB")
    cnx = mysql.connector.connect(user=sql_id, password=sql_pw, host='127.0.0.1', database=sql_db)
    return cnx

def giter(cmd, path):
    if cmd == "pull":
        comandos = ["/bin/git -C {} pull origin master"]
    elif cmd == "push":
        comandos = ["/bin/git -C {} add .", "/bin/git -C {} commit -m \"act\"",
                    "/bin/git -C {} push origin master 2>&1 | tee -a /root/log.txt"]
 
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


cnx = conexion()
cursor = cnx.cursor()
query = """select * from Actzl where pasar>0"""
cursor.execute(query)
result = cursor.fetchall()

# sequence = cursor.column_names
# print(sequence)

datos = []
ides = []
for x in result:
    datos.append({'fecha': str(x[1]), 'instruccion': x[2], 'firma': x[3]})
    ides.append(x[0])

if len(datos) > 0:

    #user = 'sistelca'
    #repo_name = 'desechosSolidos'

    path = '/home/luis/desechosSolidos'
    file_orig = "orig_data.json"
    file_orig_check = "orig_data.sha1"
    file_dest_check = "dest_data.sha1"
    giter('pull', path)
    
    #query1= """select hash_bloq from cade_bloqs order by created_at desc limit 1"""
    #cursor.execute(query1)
    #try:
    #    hash_ureg = cursor.fetchone()[0]
    #except:
    #    hash_ureg = 'vacio'

    cheq_org  = leeshas(file_orig_check)
    cheq_dest = leeshas(file_dest_check)
    
    # leer desde ultimo registro de cade_bloqs el campohash_bloq
    # para compararlo en el siguiente if

    orig = json.dumps(datos)
    check_orig = hashlib.sha1(orig.encode('utf-8')).hexdigest()

    with open(os.path.join(path, file_orig), 'w', encoding = 'utf-8') as f:
        json.dump(datos, f)

    with open(os.path.join(path, file_orig_check), 'w', encoding = 'utf-8') as f:
        f.write(check_orig)

    # hacer git
    giter('push', path)
    
    # si origen local es diferente a origen remoto y
    # remoto origen y destinos son iguales
    if cheq_dest == 'vacio' or cheq_org == cheq_dest:
        sel_pass = 0
        for y in ides:
            query = """UPDATE Actzl SET pasar={} WHERE id = {}""".format(sel_pass, y)
            cursor.execute(query)        
        
    #elif cheq_org != cheq_dest:
    #    sel_pass = 1

cnx.commit()
cursor.close()
cnx.close()
