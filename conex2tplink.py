import mysql.connector
from tplink import TippiLink

tl = TippiLink("aaaaa", "xxxxxx", "111.222.333.444")


cnx = mysql.connector.connect(user='abc', password='laumex', host='111.222.333.444', database='mirsig')
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
