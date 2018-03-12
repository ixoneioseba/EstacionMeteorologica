# CREO UN CANAL NUEVO EN EL QUE SE SUBIRAN POSTERIORMENTE LOS DATOS RECOGIDOS

#print "--> Crear conexión TCP..."
conn_TCP = httplib.HTTPSConnection("api.thingspeak.com")
conn_TCP.connect()
#print "--> Conexión TCP establecida"


#print "--> Enviando peticion HTTP"
metodo = "POST"
uri = "/channels.json?"
cabeceras = {"Host": "api.thingspeak.com",
             "Content-Type": "application/x-www-form-urlencoded"}
params = {"api_key": User_API_key,
          "description": "Canal público para el registro y visualización online de los datos atmosféricos recogidos",
          "field1": "Temperatura [ºC]",
          "field2": "Humedad [%]",
          "name": "Datos atmosféricos",
          "public_flag": "true"}
params_encoded = urllib.urlencode(params)
#print "    Params: " + params_encoded
cabeceras["Content-Length"]=len(params_encoded)
conn_TCP.request(metodo, uri, headers=cabeceras, body=params_encoded)
#print "--> Petición HTTP enviada"

#print "--> Recibiendo respuesta HTTP"
respuesta = conn_TCP.getresponse()
estatus = respuesta.status
#print "    Status:" + str(estatus)
contenido = respuesta.read()
contenido_parseado = json.loads(contenido)
Write_API_key = contenido_parseado["api_keys"][0]["api_key"]

#-------------------------------------------------------------------