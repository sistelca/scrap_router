import mysql.connector
from tplink import TippiLink
from dotenv import load_dotenv
import os
import sys

load_dotenv()
tplink_id = os.getenv("TPLINK_ID")
tplink_pw = os.getenv("TPLINK_SECRET")
tplink_hs = sys.argv[1]

if not '192.168.66.' in tplink_hs:
    print('error')
    sys.exit(1)

print('host: ', tplink_hs)

tl = TippiLink(tplink_id, tplink_pw, tplink_hs)

sql_id = os.getenv("SQL_ID")
sql_pw = os.getenv("SQL_PW")


cnx = mysql.connector.connect(user=sql_id, password=sql_pw, host='127.0.0.1', database='clientes')
cursor = cnx.cursor()

lista = tl.get_all_macs()
 
for l in lista:
    query = ("select datos_per.coduser, datos_per.nom_apell, datos_per.fech_ven, datos_red.dir_mac from datos_red, datos_per "
             "where datos_per.coduser=datos_red.coduser and datos_red.dir_mac='"+l[0]+"'")

    cursor.execute(query)
    

    for (coduser, nom_apell, fech_ven, dir_mac) in cursor:
        print("{} \t {} \t \t {} \t mac {} \t rec {} \t env {}".format(coduser, nom_apell, fech_ven, dir_mac, l[2], l[3]))

cursor.close()
cnx.close()
