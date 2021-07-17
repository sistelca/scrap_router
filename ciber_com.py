import hashlib
import json
import logging
import os
from dotenv import load_dotenv
import mysql.connector


logger = logging.getLogger(__name__)


class Datos:
    load_dotenv()
    _SQL_ID = os.environ.get("SQL_ID")
    _SQL_PW = os.environ.get("SQL_PW")
    _SQL_HOST = os.environ.get("SQL_HOST")
    _SQL_DB = os.environ.get("SQL_DB")

    _PATH_WORK = os.environ.get("PATH_WORK")
    _PATH_DATA = os.environ.get("PATH_DATA")
    _FILE_ORIG = os.environ.get("FILE_ORIG")
    _FILE_ORIG_CHECK = os.environ.get("FILE_ORIG_CHECK")
    _FILE_DEST_CHECK = os.environ.get("FILE_DEST_CHECK")
    _DATA_ORIG = os.environ.get("DATA_ORIG")
    _CHEK_ORIG = os.environ.get("CHEK_ORIG")
    _CHEK_DEST = os.environ.get("CHEK_DEST")
    

    def __init__(self) -> None:
        self.cnx = mysql.connector.connect(
            user=self._SQL_ID,
            password=self._SQL_PW,
            host=self._SQL_HOST,
            database=self._SQL_DB
        )
        # estos parametros irian en archivo .env
        self.path_work = self._PATH_WORK # ruta de scripts de comandos cibercom
        self.path = self._PATH_DATA #<- ruta de datos
        # para envio
        self.file_orig = self._FILE_ORIG              #<- local_data
        self.file_orig_check = self._FILE_ORIG_CHECK  #<- local_data_sha
        self.file_dest_check = self._FILE_DEST_CHECK  #<- remot_data_sha
        # para recibir
        self.chek_orig = self._CHEK_ORIG    # hash archivo remoto enviado
        self.chek_dest = self._CHEK_DEST    # hash archivo remoto recibido
        self.data_orig = self._DATA_ORIG    # archivo remoto enviado
        # para instanciar cursor
        self.cursor = self.cnx.cursor()

    #def set_cursor(self):
    #    return self.cursor = self.cnx.cursor()

    def giter(self, cmd):
        # la rama de prueba es main volver a master en produccion OjO
        if cmd == "pull":
            comandos = [
                "/bin/git -C {} pull origin main"
            ]
        elif cmd == "push":
            comandos = [
                "/bin/git -C {} add .", "/bin/git -C {} commit -m \"act\"",
                "/bin/git -C {} push origin main 2>&1 | tee -a /root/log.txt"
            ]
 
        for comando in comandos:
            tpcmd = comando.format(self.path)
            os.system(tpcmd)
        return True

    def leeshas(self, file):
        try:
            with open(file, encoding = "utf-8") as f:
                return f.readline()
        except:
            return "vacio"

    def lea_utl_hash(self, blq=None): # selecciona ultimo registro por fecha de cadena de bloques
        if blq==None:
            first_query = """select hash_bloq from cade_bloqs order by created_at desc limit 1"""
        else:
            first_query = """select bloq from cade_bloqs where hash_bloq=={}""".format(blq)
        self.cursor.execute(first_query)
        try:
            hash_ureg = self.cursor.fetchone()[0]
        except:
            hash_ureg = "vacio"
        return hash_ureg

    def confirmaBloq(self, cheq_dest):
        if cheq_dest != "vacio":
            confir_query = """select confirmado from cade_bloqs where hash_bloq=={}"""
            confir_query = confir_query.format(cheq_dest)
            self.cursor.execute(confir_query)
            try:
                confir = self.cursor.fetchone()[0]
            except:
                confir = 0

            if confir > 0:
                # buscar cheq_dest en cade_bloqs y leer firmas
                firmas_leidas_tx = self.lea_utl_hash(cheq_dest)
                firmas_leidas = json.loads(firmas_leidas_tx)
                sel_pass = 0
                querys = []

                for fir in firmas_leidas:
                    second_query = """UPDATE Actzl SET pasar={} WHERE firma = '{}'"""
                    second_query = second_query.format(sel_pass, fir)
                    querys.append(second_query)
                terc_query = """UPDATE cade_bloqs SET confirmado={} WHERE hash_bloq='{}'"""
                terc_query = terc_query.format(sel_pass, cheq_dest)
                querys.append(terc_query)
                logger.debug("{} ".format(self.actualizar(querys)))
        return "bloque confirmado"
    
    def cargar_envio(self):
        # que si se va a enviar
        datos = []
        firmas = []

        query = """select * from Actzl where pasar > 0"""
        self.cursor.execute(query)

        try:
            result = self.cursor.fetchall()
        except:
            result = []

        for x in result:
            datos.append(
                {
                    "fecha": str(x[1]),
                    "instruccion": x[2],
                    "firma": x[3]
                }
            )
            firmas.append(x[3])
        return [datos, firmas]
    
    def enviar(self):
        # que no se volvera a enviar
        self.giter("pull")

        cheq_org  = self.leeshas(os.path.join(self.path, self.file_orig_check))
        cheq_dest = self.leeshas(os.path.join(self.path, self.file_dest_check))

        if cheq_org == cheq_dest:
            self.confirmaBloq(cheq_dest)

        datos, firmas = self.cargar_envio()

        if len(datos) > 0:

            orig = json.dumps(datos)
            check_orig = hashlib.sha1(orig.encode("utf-8")).hexdigest()

            with open(os.path.join(self.path, self.file_orig), "w", encoding = "utf-8") as f:
                json.dump(datos, f)

            with open(os.path.join(self.path, self.file_orig_check), "w", encoding = "utf-8") as f:
                f.write(check_orig)

            self.giter("push")

            query1 = """DELETE FROM cade_bloqs WHERE confirmado>{}""".format(0)
            logger.debug(" {} ".format(self.actualizar([query1])))
            query2 = """INSERT INTO cade_bloqs (bloq, hash_bloq, hash_blq_ant) values ('{}', '{}', '{}')"""
            query2 = query2.format(json.dumps(firmas), check_orig, cheq_dest)
            logger.debug(" {} ".format(self.actualizar([query2])))

    def calcquerys(self, dt_query):
        instrucions = {
            'update': ['set', 'where'],
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

    def actualizar(self, petts):
        operation = ('; ').join(petts)

        try:
            if len(petts) > 1:
                
                result_iterator = self.cursor.execute(operation, multi=True)
                for res in result_iterator:
                    logger.debug("Running query: {} ".format(res))
                    logger.debug("Affected {} rows".format(res.rowcount))
            else:
                self.cursor.execute(operation)
            self.cnx.commit()

            return True

        except:
            self.cnx.rollback()
            return operation

    def consulta_existe(self, fireg):
        consulta = """SELECT COUNT(*) from Actzl WHERE firma = '{}'""".format(fireg)
        self.cursor.execute(consulta)
        result=self.cursor.fetchone()
        number_of_rows=result[0]
        return number_of_rows > 0

    def recibir(self):
        self.giter("pull")
        checkorg = self.leeshas(os.path.join(self.path, self.chek_orig))
        checkdes = self.leeshas(os.path.join(self.path, self.chek_dest))

        if checkorg != checkdes and checkorg != "vacio":
            with open(os.path.join(self.path, self.data_orig), encoding = "utf-8") as f:
                finalJson = json.load(f)

            firmas = []
            for registro in finalJson:
                datax = registro["instruccion"]
                dt_query = json.loads(datax.replace("u00", "\\u00"))
                fireg, querys = self.calcquerys(dt_query)
                firmas.append(registro['firma'])

                if registro["firma"] == fireg and not self.consulta_existe(registro["firma"]):
                    intru = registro['instruccion'].replace("'", "*")
                    qact  = """INSERT INTO Actzl (reg_fecha, instruc, firma, pasar)"""
                    qact += """ VALUES ('{}', '{}', '{}', 0)""".format(registro['fecha'], intru,
                                                                    registro['firma'], 0)
                    querys.append(qact)
                    logger.debug("{} ".format(self.actualizar(querys)))

                elif self.consulta_existe(registro['firma']):
                    query = """UPDATE Actzl set pasar=0 WHERE firma='{}'""".format(fireg)
                    logger.debug("{} ".format(self.actualizar([query])))

            second_query = """INSERT INTO cade_bloqs (bloq, hash_bloq, hash_blq_ant, confirmado) values ('{}', '{}', '{}', '{}')"""
            second_query = second_query.format(json.dumps(firmas), checkorg, checkdes, 0)
            logger.debug("{} ".format(self.actualizar([second_query])))

            with open(os.path.join(self.path, self.chek_dest), "w", encoding = "utf-8") as f:
                f.write(checkorg)

            self.giter("push")
            try:
                print("hola")
                #os.system(os.path.join(self.path_work, "actlz.sh"))
            except:
                pass

def main():
    datos = Datos()

    datos.enviar()
    datos.recibir()

if __name__=='__main__':
    main()