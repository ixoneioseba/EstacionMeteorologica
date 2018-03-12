#! /usr/bin/python
#-*- coding: UTF-8 -* #

import httplib  # libreria para mandar/recibir mensajes HTTP
import urllib  # librería para codificar datos
import time  # libreria para meter tiempos de espera
import Adafruit_DHT # librería para la lectura de los sensores "Adafruit" (DHT22)
import Adafruit_BMP.BMP085 as BMP085 # librería para la lectura de sensores "Adafruit" (BMP180)
import json # librería para trabajar con el formato de archivos json
import math # librería para cálculos matemáticos (sqrt...)
import RPi.GPIO as GPIO # librería para manejo de pinees GPIO


# CREO EL CANAL AUTOMATICAMENTE: # Ver script para crear canal

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
          "field6": "Velocidad Viento [ Km/h ]",
          "field7": "S. Térmica (Humedad) [ ºC ]",
          "field8": "S. Térmica (Viento) [ ºC ]",
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

# -------------------------------------------------------------------
# DESARROLLO DE PROGRAMA PARA TOMAR MEDIDA DEL ANEMOMETRO (sensor efecto Hall)

# Inicialización de Variables
dist_meas = 0.00
km_por_hora = 0
rpm = 0
intervalo = 0
sensorHALL = 14 # Nº de Pin GPIO al que está conectado el sensor HALL
pulso = 0
iniciar_timer = time.time()

def init_GPIO(): # inicializar el pin GPIO
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(sensorHALL,GPIO.IN,GPIO.PUD_UP)

def calculo_intervalo(channel): # Función CALLBACK
	global pulso, iniciar_timer, intervalo
	pulso+=1	# incrementa el pulso en 1 cuando se da una interrupción.
	intervalo = time.time() - iniciar_timer # intervalo para cada una de las vueltas dadas.
	iniciar_timer = time.time()		#Tiempo actual = iniciar el timer de nuevo		

def calcular_velocidad_viento(r_cm): # Llamar a la función con el radio en cm como parámetro.
	global pulso,intervalo,rpm,dist_km,dist_meas,km_por_seg,km_por_hora
	if intervalo !=0:							# to avoid DivisionByZero error
		rpm = 1/intervalo * 60
		circ_cm = (2*math.pi)*r_cm			# Calcular el perímetro de la circunferencia descrita por las palas del anemometro en [cm].
		dist_km = circ_cm/100000 			# Convertir cm a kM
		km_por_seg = dist_km / intervalo		# calcular KM/seg
		km_por_hora = km_por_seg * 3600		# calcular KM/h
		dist_meas = (dist_km*pulso)*1000	# medida de distancia en metros
		return km_por_hora
def init_interrupt(): # Espera a detectar evento = flanco en el pin sensor hall
	GPIO.add_event_detect(sensorHALL, GPIO.FALLING, callback = calculo_intervalo, bouncetime = 20)

init_GPIO() # Inicializo pin GPIO
init_interrupt() # Inicializo Interrupción
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
    print 'temp =' + str(temperatura)
# Calcular la velocidad del viento [KM/H]
    km_por_hora = calcular_velocidad_viento(10.5) # Velocidad_viento (10.5 cm es el radio de las palas)
    #print ("Velocidad viento: " + str(km_por_hora))
    

# Calcular la temperatura del Punto de Rocio [ºC]
    PuntoRocio=((humedad/100)**(0.125))*(112+0.9*temperatura)+(0.1*temperatura)-112
    print ("Punto de Rocio: " + str(PuntoRocio))
    
# Calcular la sensación térmica (2 métodos)
# Sensación térmica por HUMEDAD (temperatura, humedad)
    temperaturaF=(temperatura*1.8)+32
    HeatIndex=(0.5*(temperaturaF+61+((temperaturaF-68)*1.2)+(humedad*0.094))-32)/1.8
    print ("Sensacion termica por calor : " + str(HeatIndex))
    
# Sensación térmica por VIENTO (temperatura, viento)
    if type(km_por_hora) != float :
        # Entra en este bucle cuando NO hay medida de viento. Recibimos un NoneType del sensorHALL
        WindChill = (35.74+0.6125*temperaturaF-32)/1.8
    else: 
        mph = km_por_hora**0.62
        WindChill = (35.74+0.6125*temperaturaF-35.75*(mph**0.16)+0.4275*temperaturaF*(mph**0.16)-32)/1.8
    print ("Sensacion termica por Viento : " +str(WindChill))

#-------------------------------------------------------------------------------------------------
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
              "field5": altitud,
              "field6": km_por_hora,
              "field7": HeatIndex,
              "field8": WindChill
              }

    params_encoded = urllib.urlencode(params)
    #print "    Params: " + params_encoded
    cabeceras["Content-Length"]=len(params_encoded)
    conn_TCP.request(metodo, uri, headers=cabeceras, body=params_encoded)
    #print "--> Petición HTTP enviada"

    #print "--> Recibiendo respuesta HTTP"
    respuesta = conn_TCP.getresponse()
    #estatus = respuesta.status
    #print "    Status:" + str(estatus)
    contenido = respuesta.read()
    #print "    Contenido:" + contenido
    # Duerme 15 segundos
    time.sleep(15)



