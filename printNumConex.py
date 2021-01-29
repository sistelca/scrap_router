# # previo al lanzamiento obtener el siguiente parametro
# comm: xwininfo | grep "Window id:"
# resp: xwininfo: Window id: 0x200008c "22m:42s - FreeBitco.in - Win free bitcoins every hour! - Mozilla Firefox"
# comm: printf %i 0x200008c
# resp: 37748876

import os
import time
from datetime import datetime
from miner  import minerPdf

#os.system("/usr/bin/xdotool mousemove 300 30 click 1")

def imprime_Pdf():

    os.system("/usr/bin/firefox --new-window http://192.168.66.32")
    time.sleep(9)
    os.system("/usr/bin/xdotool key KP_Enter")

    # selecciona del menu
    os.system("/usr/bin/xdotool mousemove 50 390 click 1")
    time.sleep(2)
    os.system("/usr/bin/xdotool mousemove 50 495 click 1")
    time.sleep(2)


    # imprime
    os.system("/usr/bin/xdotool mousemove 50 90 click 1")
    time.sleep(2)
    os.system("/usr/bin/xdotool mousemove 40 305 click 1")
    time.sleep(2)
    os.system("/usr/bin/xdotool mousemove 350 380 click 1")
    time.sleep(2)
    os.system("/usr/bin/xdotool mousemove 960 770 click 1")
    time.sleep(2)
    os.system("/usr/bin/xdotool mousemove 750 590 click 1")
    time.sleep(2)
    os.system("/usr/bin/xdotool mousemove 210 110 click 1")



i=0

while True:
    imprime_Pdf()
    if 'prueba.pdf' in os.listdir('../'):
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        try:
            conecta2 = minerPdf.extract_text_from_pdf('../prueba.pdf')
            print(timestamp, conecta2, '\n')
            with open('resultados_tplink.txt', 'a') as resulta2:
                resulta2.write(str(timestamp)+'\t'+conecta2[conecta2.index(':')+1:]+ '\n')
        except:
            pass
        i += 1
        #if i > 10:
        #    break
        time.sleep(47)




