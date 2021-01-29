import requests
from urllib.parse import quote
import base64
import re
import time
from datetime import datetime

#import os
#import shutil

#if not 'conex2tplink.txt' in os.listdir('/var/www/html/'):
#    shutil.copyfile('conex2tplink.txt', '/var/www/html/conex2tplink.txt')

class TippiLink:
    def __init__(self, username, password, host="192.168.0.1"):
        self._username = username
        self._password = password
        self._host = host

    def _get_headers(self):
        headers = {
            'Referer': 'http://%s/userRpm/MenuRpm.htm' % self._host,
            'Authorization': self._auth_header(),
        }
        return headers

    def _auth_header(self):
        auth_bytes = bytes(self._username+':'+self._password, 'utf-8')
        auth_b64_bytes = base64.b64encode(auth_bytes)
        auth_b64_str = str(auth_b64_bytes, 'utf-8')
        auth_str = quote('Basic {}'.format(auth_b64_str))
        return auth_str


tl = TippiLink("luis", "AmE3024OT1", "192.168.66.32")
ini = 'wlanHostPara = new Array('
fin = ');'

i = 0
while True:
    try:
        response = requests.get('http://%s/userRpm/%s.htm' % (tl._host, 'WlanStationRpm.htm'), headers=tl._get_headers())
        content = response.content
        now = datetime.now()
        timestamp = datetime.timestamp(now)

        lista = str(content)[str(content).index(ini)+len(ini):str(content).index(fin)].replace('\\n', '').split(',')

        #print(timestamp, lista[5])
        with open('/var/www/html/conex2tplink.txt', 'a') as resulta2:
            resulta2.write(str(timestamp)+'\t'+lista[5]+'\n')

    except:
        pass

    time.sleep(50)
    #i += 1
    #if i > 10:
    #    break
