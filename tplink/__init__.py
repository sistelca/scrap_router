import requests
from urllib.parse import quote
import base64
import time
from datetime import datetime

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
    
    def _get_mac_from_page(self, pageName):
        
        try:

            response = requests.get('http://%s/userRpm/%s.htm' % (self._host, pageName), headers=self._get_headers())
            content = response.content

            ini = 'hostList = new Array('
            fin = ');'

            texto = str(content)[str(content).index(ini)+len(ini)+2:].replace('\\n', '').replace(', 0,0 ', '')
            texto = texto[:texto.index(fin)].replace('-', ':').lower()
                        
            lista = [l.replace("\"", "").replace(" ", "") for l in texto.split(',')]
            nueva_lista = [lista[i:i+4] for i in range(0, len(lista), 4) if lista[i+1] in ['0', '1', '8']]
                                                
            return nueva_lista
                                                                    
        except:
            pass   # return "Error"
    
    def get_all_macs(self):
        page = '1'
        macs = []
        mac_stat = []

        while True:
            arr_in = self._get_mac_from_page("WlanStationRpm.htm?Page="+page)
            arr = [l[0] for l in arr_in]
            page = str(int(page) + 1)

            if set(arr).issubset(set(macs)):
                break
            else:
                macs.extend(arr)
                mac_stat.extend(arr_in)

        mac_stat.sort(key=lambda x:int(x[2]), reverse=True)
        macs = [m[0] for m in mac_stat]

        return mac_stat   #macs
    
    def estadisticas(self):
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        ini = 'wlanHostPara = new Array('
        ini1 = 'statistList = new Array('
        fin = ');'

        try:
            # numero de conectados
            response = requests.get('http://%s/userRpm/%s.htm' % (self._host, 'WlanStationRpm.htm'), headers=self._get_headers())
            content = response.content
            lista = str(content)[str(content).index(ini)+len(ini):str(content).index(fin)].replace('\\n', '').split(',')
            nconx = lista[5]

            # enviados y recibidos
            response = requests.get('http://%s/userRpm/%s.htm' % (self._host, 'StatusRpm.htm'), headers=self._get_headers())
            content = response.content
            texto = str(content)[str(content).index(ini1)+len(ini1)+2:]
            statistList = texto[:texto.index(fin)].split(',')

            b_rec = statistList[0]
            b_env = statistList[1]
            
            return [timestamp, nconx, b_rec, b_env]
        except:
            pass   # return "Error"
        
    def restart_router(self):
        params = (('Reboot', 'Reboot'),)
        try:
            res = requests.get('http://%s/userRpm/SysRebootRpm.htm' % self._host,
                                headers=self._get_headers(), params=params)
        except:
            pass
