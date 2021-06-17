import mysql.connector
from dotenv import load_dotenv
import os
import json
import hashlib
import requests
# import base64

# def leeactzl(user, repo_name, path_to_file):
#     json_url ='https://api.github.com/repos/{}/{}/contents/{}'.format(user, repo_name,
#                                                                       path_to_file)
#     response = requests.get(json_url) #get data from json file located at specified URL 

#     if response.status_code == requests.codes.ok:
#         jsonResponse = response.json()  # the response is a JSON
#         #the JSON is encoded in base 64, hence decode it
#         content = base64.b64decode(jsonResponse['content'])
#         #convert the byte stream to string
#         jsonString = content.decode('utf-8')
#         try:
#             return json.loads(jsonString)
#         except:
#              return jsonString
 
#     else:
#         return 'Content was not found.'


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


cnx = conexion()
cursor = cnx.cursor()
query = ("select * from Actzl where pasar=2")
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

    cheq_org  = leeshas(user, repo_name, file_orig_check)
    cheq_dest = leeshas(user, repo_name, file_dest_check)

    orig = json.dumps(datos)
    check_orig = hashlib.sha1(orig.encode('utf-8')).hexdigest()

    # si origen local es diferente a origen remoto y
    # remoto origen y destinos son iguales
    if check_orig != cheq_org and cheq_org == cheq_dest:
    
        with open(os.path.join(path, file_orig), 'w', encoding = 'utf-8') as f:
            json.dump(datos, f)

        with open(os.path.join(path, file_orig_check), 'w', encoding = 'utf-8') as f:
            f.write(check_orig)

        # hacer git
        giter('push', path)

        for x in ides:
            query = ("UPDATE Actzl SET pasar=0 WHERE id = {}").format(x)
            cursor.execute(query)

cnx.commit()
cursor.close()
cnx.close()