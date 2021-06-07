import requests
import base64
import json
import subprocess
import os

def leeactzl(user, repo_name, path_to_file):
    json_url ='https://api.github.com/repos/{}/{}/contents/{}'.format(user, repo_name,
                                                                      path_to_file)
    response = requests.get(json_url) #get data from json file located at specified URL 

    if response.status_code == requests.codes.ok:
        jsonResponse = response.json()  # the response is a JSON
        #the JSON is encoded in base 64, hence decode it
        content = base64.b64decode(jsonResponse['content'])
        #convert the byte stream to string
        jsonString = content.decode('utf-8')
        try:
            return json.loads(jsonString)
        except:
             return jsonString
 
    else:
        return 'Content was not found.'

os.chdir('/home/luis/cibercom/desechosSolidos')
user = 'sistelca'
repo_name = 'desechosSolidos'
path_to_file = "resplientes.sha1"

texto_r = leeactzl(user, repo_name, path_to_file)
chsum_r = texto_r.split(' ')[0]

result = subprocess.run(['/bin/sha1sum', 'resplientes.sql'], stdout=subprocess.PIPE)
texto_l = result.stdout.decode('utf-8')

chsum_l = texto_l.split(' ')[0]

if chsum_l != chsum_r and texto_r != 'Content was not found.':
    os.system("ls -l > ./prueba.txt")


