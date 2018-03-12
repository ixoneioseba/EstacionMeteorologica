#-*- coding: UTF-8 -* #

import httplib  # libreria para mandar/recibir mensajes HTTP
import urllib  #librería para codificar datos
import time  #libreria para meter tiempos de espera
import Adafruit_DHT #Librería para la lectura de los sensores "Adafruit"
import json # librería para trabajar con el formato de archivos json

# CREO EL CANAL AUTOMATICAMENTE:

User_API_key = "GJE4UHZ8SZPL4OM9"
Write_API_key =""
Read_API_key = ""

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
          "field1": "Temperatura [ ºC ]",
          "field2": "Humedad [ % ]",
          "field3": "Punto de Rocio [ ºC ]",
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
#CONFIGURACION DEL SENSOR DHT11

# Configuracion del tipo de sensor DHT22

sensor = Adafruit_DHT.DHT22

# Configuracion del puerto GPIO al cual esta conectado  (GPIO 27)
pin = 13

# Obtiene la humedad y la temperatura desde el sensor
while True :
    humedad, temperatura = Adafruit_DHT.read_retry(sensor, pin)

# Calcular la temperatura del Punto de Rocio [ºC]
PuntoRocio=((humedad/100)**(1/8)*(112+0.9*temperatura)+(0.1*temperatura)-112)


    #print "--> Subiendo datos a ThingSpeak"
    #print "--> Enviando peticion HTTP"
    metodo = "POST"
    uri = "/update.json"
    cabeceras = {"Host": "api.thingspeak.com",
                 "Content-Type": "application/x-www-form-urlencoded"}
    params = {"api_key": Write_API_key,
              "field1": temperatura,
              "field2": humedad}

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
    #print "    Contenido:" + contenido
    # Duerme 15 segundos
    time.sleep(15)



