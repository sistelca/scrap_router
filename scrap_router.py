from tplink import TippiLink
import time

import os
#import shutil

if not 'conex2tplink.txt' in os.listdir('/var/www/html/'):
#    shutil.copyfile('conex2tplink.txt', '/var/www/html/conex2tplink.txt')
    with open('/var/www/html/conex2tplink.txt', 'w') as resulta2:
        resulta2.write('timestamp'+'\t'+'N_conx'+'\t'+'b_reci'+'\t'+'b_env'+'\n')


from dotenv import load_dotenv
import os

load_dotenv()
tplink_id = os.getenv("TPLINK_ID")
tplink_pw = os.getenv("TPLINK_SECRET")

tl = TippiLink(tplink_id, tplink_pw, "192.168.66.32")
ini = 'wlanHostPara = new Array('
ini1 = 'statistList = new Array('
fin = ');'

estado = 0
i = 0
while True:
    try:

        lista = tl.estadisticas()
        
        with open('/var/www/html/conex2tplink.txt', 'a') as resulta2:
            resulta2.write(str(lista[0])+'\t'+lista[1]+'\t'+lista[2]+'\t'+lista[3]+'\n')
            
        if int(lista[1]) < 10 and estado ==0 :
            estado = 1
            tl.restart_router()
        elif int(lista[1]) > 10:
            estado = 0

    except:
        pass

    time.sleep(50)
    #i += 1
    #if i > 10:
    #    break
    