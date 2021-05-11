import mysql.connector
from dotenv import load_dotenv
import os
import sys
import requests
import re


load_dotenv()
user_name = os.getenv("BFL_ID")
user_pasw = os.getenv("BFL_PW")
bfl_hs = sys.argv[1]

if not '192.168.66.' in bfl_hs:
    print('error')
    sys.exit(1)

url ='http://{}/Status_Wireless.asp'.format(bfl_hs)

r = requests.get(url, auth=(user_name, user_pasw))

def elimrep(a):
    b = [a.count(x) for x in a]
    c = [x[0] for x in zip(a, b) if x[1] == 1]
    return c

data = r.text

p = re.compile(r'(?:[0-9a-fA-F]:?){12}')

macs = []
found = re.findall(p, data)
for a in found:
    macs.append(a)

# las repetidas son la mac del router
macs = elimrep(macs)

sql_id = os.getenv("SQL_ID")
sql_pw = os.getenv("SQL_PW")

cnx = mysql.connector.connect(user=sql_id, password=sql_pw, host='127.0.0.1', database='clientes')
cursor = cnx.cursor()

for l in macs:
    print(l)
    query = ("select datos_per.coduser, datos_per.nom_apell, datos_per.fech_ven, datos_red.dir_mac from datos_red, datos_per "
             "where datos_per.coduser=datos_red.coduser and datos_red.dir_mac like  '%"+l+"%'")

    cursor.execute(query)
    

    for (coduser, nom_apell, fech_ven, dir_mac) in cursor:
        print("{} \t {} \t \t {} \t mac {}".format(coduser, nom_apell, fech_ven, dir_mac, l[2], l[3]))


cursor.close()
cnx.close()
