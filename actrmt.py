import mysql.connector
from dotenv import load_dotenv
import os
import json
import hashlib
import requests


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


def conexion():
    load_dotenv()

    sql_id = os.getenv("SQL_ID")
    sql_pw = os.getenv("SQL_PW")
    #sql_hs = os.getenv("SQL_HOST")
    sql_db = os.getenv("SQL_DB")
    cnx = mysql.connector.connect(user=sql_id, password=sql_pw, host='127.0.0.1', database=sql_db)
    return cnx


user = 'sistelca'
repo_name = 'desechosSolidos'
path = '/home/luis/desechosSolidos'
file_orig = "orig_data.json"
file_orig_check = "orig_data.sha1"
file_dest_check = "dest_data.sha1"

cheq_org  = leeactzl(user, repo_name, file_orig_check)
cheq_dest = leeactzl(user, repo_name, file_dest_check)

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
    orig = json.dumps(datos)
    check_orig = hashlib.sha1(orig.encode('utf-8')).hexdigest()

    try:
         with open(os.path.join(path, 'orig_data.sha1'), 'r', encoding = 'utf-8') as f:
                ch = f.readline()
    except:
        ch ='vacio'

    if check_orig != ch:
        with open(os.path.join(path, file_orig), 'w', encoding = 'utf-8') as f:
            json.dump(datos, f)

        with open(os.path.join(path, file_orig_check), 'w', encoding = 'utf-8') as f:
            f.write(check_orig)
            
        # hacer git

        if cheq_org == cheq_dest and cheq_org != 'Content was not found.':

            for x in ides:
                query = ("UPDATE Actzl SET pasar=0 WHERE id = {}").format(x)
                cursor.execute(query)

cnx.commit()
cursor.close()
cnx.close()

