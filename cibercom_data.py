import mysql.connector
from dotenv import load_dotenv
import os
import json
import hashlib
import requests

def conexion():
    load_dotenv()

    sql_id = os.getenv("SQL_ID")
    sql_pw = os.getenv("SQL_PW")
    cnx = mysql.connector.connect(user=sql_id, password=sql_pw, host='127.0.0.1', database='clientes')
    return cnx

def giter(cmd, path):
    if cmd == "pull":
        comandos = ["/bin/git -C {} pull origin master"]
    elif cmd == "push":
        comandos = ["/bin/git -C {} add .", "/bin/git -C {} commit -m \"act\"",
                    "/bin/git -C {} push origin master 2>&1 | tee -a /root/log.txt"]
 
    for comando in comandos:
        tpcmd = comando.format(path)
        os.system(tpcmd)
    return True

def leeshas(file):
    try:
        with open(file, encoding = 'utf-8') as f:
            return f.readline()
    except:
        return 'vacio'


class Datos:
    def __init__(self) -> None:
        self.cnx = conexion()
        # estos parametros irian en archivo .env
        self.path_work = '/home/luis/cibercom'
        self.path = '/home/luis/desechosSolidos' #<- ruta
        # para envio
        self.file_orig = "orig_data.json"        #<- local_data
        self.file_orig_check = "orig_data.sha1"  #<- local_data_sha
        self.file_dest_check = "dest_data.sha1"  #<- remot_data_sha

        # para recibir
        self.chek_orig = 'prometea_data.sha1'
        self.chek_dest = 'ok_prometea.sha1'
        self.data_orig = 'prometea_data.json'

    def lea_utl_hash(self):
        cursor = self.cnx.cursor()
        query1= """select hash_bloq from cade_bloqs order by created_at desc limit 1"""
        cursor.execute(query1)
        try:
            hash_ureg = cursor.fetchone()[0]
        except:
            hash_ureg = 'vacio'
        return hash_ureg

    def enviar(self):
        cursor = self.cnx.cursor()
        query = """select * from Actzl where pasar>0"""
        cursor.execute(query)
        result = cursor.fetchall()

        # sequence = cursor.column_names
        # print(sequence)

        datos = []
        ides = []
        for x in result:
            datos.append({'fecha': str(x[1]), 'instruccion': x[2], 'firma': x[3]})
            ides.append(x[0])

        if len(datos) > 0:

            #user = 'sistelca'
            #repo_name = 'desechosSolidos'

            giter('pull', self.path)
            
            hash_ureg = self.lea_utl_hash(self)

            cheq_org  = leeshas(self.file_orig_check)
            cheq_dest = leeshas(self.file_dest_check)
            
            # leer desde ultimo registro de cade_bloqs el campohash_bloq
            # para compararlo en el siguiente if

            orig = json.dumps(datos)
            check_orig = hashlib.sha1(orig.encode('utf-8')).hexdigest()

            with open(os.path.join(self.path, self.file_orig), 'w', encoding = 'utf-8') as f:
                json.dump(datos, f)

            with open(os.path.join(self.path, self.file_orig_check), 'w', encoding = 'utf-8') as f:
                f.write(check_orig)

            # hacer git
            giter('push', self.path)
            
            # si origen local es diferente a origen remoto y
            # remoto origen y destinos son iguales
            if cheq_dest == 'vacio' or cheq_org == cheq_dest:
                sel_pass = 0
                for y in ides:
                    query = """UPDATE Actzl SET pasar={} WHERE id = {}""".format(sel_pass, y)
                    cursor.execute(query)

                query2 = """INSERT INTO cade_bloqs (bloq, hash_bloq, hash_blq_ant) values ({}, {}, {})""".format(orig, check_orig, hash_ureg)
                cursor.execute(query2)
            #elif cheq_org != cheq_dest:
            #    sel_pass = 1

    def calcquerys(dt_query):

        instrucions =  {'update': ['set', 'where'],
                    'insert into': ['(', ') values'],
                    'delete from': ['where', 'todo']
                }

        regq = ''
        query = []

        for y in dt_query.keys():
            z = dt_query[y]
            asi = z['op'].lower()
            gna = instrucions[asi][0]
            if instrucions[asi][1] != 'todo':
                fl = instrucions[asi][1]
            else:
                fl = ''

            regq += z['op'] +' ' + y + ' ' + gna + z['set'] + fl + z['filtro']
            query.append(z['op'] +' ' + y + ' ' + gna.upper() + z['set'] + fl.upper() + z['filtro'])
            
        retregq = hashlib.sha1(regq.lower().encode('utf-8')).hexdigest()

        return retregq, query

    def actualiza(self, petts):

        operation = ('; ').join(petts)

        try:
            cursor = self.cnx.cursor()
            if len(petts) > 1:
                
                result_iterator = cursor.execute(operation, multi=True)
                #i = 0

                for res in result_iterator:
                    print("Running query: ", res)
                    print(f"Affected {res.rowcount} rows" )
                    #i += 1
                    #if i == len(petts): # evitar RuntimeError:
                    #    break # generator raised StopIteration

            else:

                cursor.execute(operation)
            self.cnx.commit()

            return True

        except:
            self.cnx.close()
            return operation


    def consulta_existe(self, fireg):

        consulta = """SELECT COUNT(*) from Actzl WHERE firma = '{}'""".format(fireg)
        cursor = self.cnx.cursor()
        cursor.execute(consulta)
        result=cursor.fetchone()
        number_of_rows=result[0]
        return number_of_rows > 0


    def recibir(self):
        giter("pull", self.path)

        checkorg = leeshas(os.path.join(self.path, self.chek_orig))
        checkdes = leeshas(os.path.join(self.path, self.chek_dest))

        if checkorg != checkdes and checkorg != 'vacio':

            with open(os.path.join(self.path, self.data_orig), encoding = 'utf-8') as f:
                finalJson = json.load(f)

            for registro in finalJson:
                datax = registro['instruccion']
                dt_query = json.loads(datax.replace('u00', '\\u00'))
                fireg, querys = self.calcquerys(dt_query)

                if registro['firma'] == fireg and not self.consulta_existe(registro['firma']):

                    # valor 0 en Actzl.pasar => query recibido no se sube a nube,
                    # * en vez de ' inutiliza query descargado
                    intru = registro['instruccion'].replace("'", "*")
                    qact  = """INSERT INTO Actzl (reg_fecha, instruc, firma, pasar)"""
                    qact += """ VALUES ('{}', '{}', '{}', 0)""".format(registro['fecha'], intru,
                                                                    registro['firma'], 0)
                    querys.append(qact)

                    print(self.actualiza(querys))

                elif self.consulta_existe(registro['firma']):
                    query = """UPDATE Actzl set pasar=0 WHERE firma='{}'""".format(fireg)
                    print(self.actualiza([query]), '\n')

            query2 = """INSERT INTO cade_bloqs (bloq, hash_bloq, hash_blq_ant) values ({}, {}, {})""".format(json.dumps(finalJson), checkorg, self.lea_utl_hash(self))
            print(self.actualiza([query2]), '\n')

            with open(os.path.join(self.path, self.chek_dest), 'w', encoding = 'utf-8') as f:
                f.write(checkorg)

            giter("push", self.path)
            os.system(os.path.join(self.path_work, 'actlz.sh'))
