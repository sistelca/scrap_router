import mysql.connector
from tplink import TippiLink

tl = TippiLink("luis", "AmE3024OT1", "192.168.66.32")


cnx = mysql.connector.connect(user='root', password='prometea2008', host='127.0.0.1', database='clientes')
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
