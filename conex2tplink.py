import mysql.connector
from tplink import TippiLink
from dotenv import load_dotenv
import os

load_dotenv()
tplink_id = os.getenv("TPLINK_ID")
tplink_pw = os.getenv("TPLINK_SECRET")

tl = TippiLink(tplink_id, tplink_pw, "192.168.66.32")

sql_id = os.getenv("SQL_ID")
sql_pw = os.getenv("SQL_PW")


cnx = mysql.connector.connect(user=sql_id, password=sql_pw, host='127.0.0.1', database='clientes')
cursor = cnx.cursor()

lista = tl.get_all_macs()
 
for l in lista:
    query = ("select datos_per.coduser, datos_per.nom_apell, datos_red.dir_mac from datos_red, datos_per "
             "where datos_per.coduser=datos_red.coduser and datos_red.dir_mac='"+l+"'")

    cursor.execute(query)
    

    for (coduser, nom_apell, l) in cursor:
        print("{}, {} mac {}".format(coduser, nom_apell, l))

cursor.close()
cnx.close()
