#-*- coding: UTF-8 -* #

import httplib  # libreria para mandar/recibir mensajes HTTP
import urllib  # librería para codificar datos
import time  # libreria para meter tiempos de espera
import Adafruit_DHT # librería para la lectura de los sensores "Adafruit" (DHT22)
import Adafruit_BMP.BMP085 as BMP085 # LIbrería para la lectura de sensores "Adafruit" (BMP180)
import json # librería para trabajar con el formato de archivos json
import math # librería para cálculos matemáticos (sqrt...)


# CREO EL CANAL AUTOMATICAMENTE:

User_API_key = "GJE4UHZ8SZPL4OM9"
Write_API_key =""
Read_API_key = ""
Channel_ID = "391121"

#ACTUALIZO DATOS EN EL CANAL CREADO

#print "--> Crear conexión TCP..."
conn_TCP = httplib.HTTPSConnection("api.thingspeak.com")
conn_TCP.connect()
#print "--> Conexión TCP establecida"

#print "--> Enviando peticion HTTP"
metodo = "PUT"
uri = "/channels/" + Channel_ID + ".json"
cabeceras = {"Host": "api.thingspeak.com",
             "Content-Type": "application/x-www-form-urlencoded"}
params = {"api_key": User_API_key,
          "description": "Canal público para el registro y visualización online de los datos atmosféricos recogidos",
          "field1": "Temperatura [ ºC ]",
          "field2": "Humedad [ % ]",
          "field3": "Punto de Rocio [ ºC ]",
          "field4": "Presión [ mbar ]",
          "field5": "Altitud [ m ]",
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
print "    Status:" + str(estatus)
contenido = respuesta.read()
contenido_parseado = json.loads(contenido)
Write_API_key = contenido_parseado["api_keys"][0]["api_key"]

# -------------------------------------------------------------------
# CONFIGURACION DE LOS SENSORES 

#DHT22  -> Temperatura y Humedad relativa
#BMP180 -> Presión y Altitud

# Configuracion del tipo de sensores
sensorDHT22 = Adafruit_DHT.DHT22
sensorBMP180 = BMP085.BMP085()

# Configuracion del pin GPIO al cual esta conectado el sensor DHT22 (GPIO 4)
pin = 4
#-------------------------------------------------------------------

# OBTENCION DE PARÁMETROS
# Obtiene la humedad y la temperatura desde el sensor DHT22
# Obtiene la presión y la altitud desde el sensor BMP180
while True :
    humedad, temperatura = Adafruit_DHT.read_retry(sensorDHT22, pin)
    altitud = sensorBMP180.read_altitude()
    presion = sensorBMP180.read_pressure()

# Calcular la temperatura del Punto de Rocio [ºC]
    PuntoRocio=(humedad/100)**(1/8)*(112+0.9*temperatura)+(0.1*temperatura)-112
    #print ("Punto de Rocio:" + str(PuntoRocio))

# SUBIDA DE DATOS A LA PLATAFORMA IoT
    #print "--> Subiendo datos a ThingSpeak"
    #print "--> Enviando peticion HTTP"
    metodo = "POST"
    uri = "/update.json"
    cabeceras = {"Host": "api.thingspeak.com",
                 "Content-Type": "application/x-www-form-urlencoded"}
    params = {"api_key": Write_API_key,
              "field1": temperatura,
              "field2": humedad,
              "field3": PuntoRocio,
              "field4": presion,
              "field5": altitud}

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



