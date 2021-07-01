import json
import base64
import requests
import re

from flask import Flask, request, make_response, redirect
from flask_cors import CORS

app = Flask(__name__) 
CORS(app)


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
    

@app.route("/", methods=['GET', 'POST']) 
def home_view(): 

    user = 'sistelca'
    repo_name = 'midir'
    path_to_file = 'ip.txt'

    dir_ip = leeactzl(user, repo_name, path_to_file)

    ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', dir_ip )[0]

    return redirect('http://'+ip, code=302)
