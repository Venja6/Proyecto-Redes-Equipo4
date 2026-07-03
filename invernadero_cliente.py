from dataclasses import dataclass
import random
import time
import json
import urllib.request

@dataclass
class dato:
    valor: int
    tipo: str
    

humedad_ambiente = dato(75.0, "%")
co2 = dato(900, "ppm") 
temperatura_ambiente = dato(23, "C°")
radiacion_solar = dato(30000, "lux")
humedad_suelo = dato(55.0, "%")
pH_agua = dato(5.5, "pH")

tipo = input("Modo automatico = 0 / Modo manual para probar eventos = 1")

while(True):
    humedad_ambiente.valor = humedad_ambiente.valor + (random.randint(1, 2) * random.choice([1, -1]))
    co2.valor = co2.valor + (random.randint(0, 100) * random.choice([1, -1]))
    temperatura_ambiente.valor = temperatura_ambiente.valor + (1 * random.choice([1, -1]))
    radiacion_solar.valor = radiacion_solar.valor + (random.randint(0, 5000) * random.choice([1, -1]))
    humedad_suelo.valor = humedad_suelo.valor + (random.randint(1, 2) * random.choice([1, -1]))
    pH_agua.valor = round(pH_agua.valor + (0.1 * random.choice([1, -1])), 1)
    
    nombres = ["Humedad Amb.", "CO2", "Temp. Amb.", "Radiación", "Humedad Suelo", "pH Agua"]
    
    valores = [humedad_ambiente, co2, temperatura_ambiente, radiacion_solar, humedad_suelo, pH_agua]
    limite_inferior = [35, 300,  10, 10000, 20, 4.5]
    limite_superior = [90, 2500, 35, 50000, 85, 7.5]
    
    paquete_datos = {}
    for i in range(len(valores)):
        paquete_datos[nombres[i]] = {
            "valor": valores[i].valor,
            "tipo": valores[i].tipo
        }
        
    
    if tipo == "1":
        evento = input("eventos: 0 = nada, 1/-1 = crisis humedad, 2/-2 = crisis co2, 3/-3 = crisis temperatura, 4/-4 = crisis radiacion, 5/-5 = crisis humedad suelo, 6/-6 = crisis pH agua \n")
        evento = int(evento)
        if evento == 1 or evento == -1:
            humedad_ambiente.valor == humedad_ambiente.valor + 100 * evento
        if evento == 2 or evento == -2:
            co2.valor == co2.valor + 1000 * evento
        if evento == 3 or evento == -3:
            temperatura_ambiente.valor == temperatura_ambiente.valor + 10 * evento
        if evento == 4 or evento == -4:
            radiacion_solar.valor == radiacion_solar.valor + 10000 * evento
        if evento == 5 or evento == -5:
            humedad_suelo.valor == humedad_suelo.valor + 100 * evento
        if evento == 6 or evento == -6:
            pH_agua.valor == pH_agua.valor + 1 * evento
    
    for i in range(len(valores)):
        sensor = valores[i]
        if sensor.valor < limite_inferior[i]:
            print(f"ALERTA: {nombres[i]} fuera de rango inferior: {sensor.valor} {sensor.tipo}")
        elif sensor.valor > limite_superior[i]:
            print(f"ALERTA: {nombres[i]} fuera de rango superior: {sensor.valor} {sensor.tipo}")
            
    mensaje_json = json.dumps(paquete_datos)
    datos_en_bytes = mensaje_json.encode('utf-8')

    url = "http://192.168.1.12:5006/datos"

    peticion = urllib.request.Request(url, data=datos_en_bytes, method='POST')

    peticion.add_header('Content-Type', 'application/json')
    
    
    try:
        respuesta = urllib.request.urlopen(peticion)
        if respuesta.status == 200:
            print("Datos enviados con éxito vía HTTP.")
        else:
            print(f"El servidor respondió con código: {respuesta.status}")
            
    except urllib.error.URLError as e:
        print(f"Fallo al conectar con el servidor: {e.reason}")
        
            
    for i in range(len(valores)):
        sensor = valores[i]
        print(f"{nombres[i]}: {sensor.valor} {sensor.tipo}")
        
    
        
    time.sleep(1)
        

    
