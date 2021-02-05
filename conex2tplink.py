import mysql.connector
cnx = mysql.connector.connect(user='root', password='prometea2008', host='127.0.0.1', database='clientes')
cursor = cnx.cursor()

lista = ['a8:c8:3a:75:22:0b',  '0e:8a:0f:08:3b:2a',   '60:1d:91:c1:8a:6a',
   'fc:a6:21:36:63:de',  '80:9b:20:db:f5:c0',  '3c:05:18:38:6c:b9',
   '78:36:90:b2:0c:2f',  '44:6d:57:df:38:87',  'bc:98:df:6d:17:33',
   'c0:17:4d:a0:20:b5',  'bc:44:86:90:fc:ca',  'bc:25:e0:92:da:4c',
   'a2:01:3d:d1:f2:33',  '0c:ce:f6:6d:8f:3f',  'd8:55:a3:ba:9b:4f',
   'f8:1a:67:cf:ef:82',  '00:8a:0f:05:57:66',  '0c:8f:ff:a2:ae:4c',
   'bc:98:df:62:b0:d0',  'b8:ae:ed:e4:3d:27',  '0c:ce:f6:8a:a5:c7',
   '60:14:66:b0:53:ab',  'b0:c1:9e:eb:83:30',  '60:14:66:b5:7e:5e',
   'bc:98:df:43:d2:b5',  '94:27:90:5a:8b:e8',  '00:72:0d:39:51:da',
   '90:f6:52:e1:95:4e',  'e0:aa:96:89:9b:5e']
 
for l in lista:
    query = ("select datos_per.coduser, datos_per.nom_apell, datos_red.dir_mac from datos_red, datos_per "
             "where datos_per.coduser=datos_red.coduser and datos_red.dir_mac='"+l+"'")

    cursor.execute(query)
    

    for (coduser, nom_apell, l) in cursor:
        print("{}, {} mac {}".format(coduser, nom_apell, l))

cursor.close()
cnx.close()
