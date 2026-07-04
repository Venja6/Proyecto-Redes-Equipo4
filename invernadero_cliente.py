from dataclasses import dataclass
import random
import time
import json
import urllib.request
import ssl
@dataclass
class dato:
    """
    Estructura de datos para representar la lectura de un sensor.
    
    Atributos:
        valor (int/float): La magnitud de la medición actual.
        tipo (str): La unidad de medida (e.g., "%", "C°", "ppm").
    """
    valor: float
    tipo: str
    

# 1. Inicialización de Sensores Base

humedad_ambiente = dato(75.0, "%")
co2 = dato(900, "ppm") 
temperatura_ambiente = dato(23.0, "C°")
radiacion_solar = dato(30000, "lux")
humedad_suelo = dato(55.0, "%")
pH_agua = dato(5.5, "pH")

print("--- Inicializando Nodo Simulado de Invernadero ---")
tipo = input("Seleccione modo (0 = Automático, 1 = Manual para inyectar crisis): ")


# 2. Ciclo Principal de Monitoreo

while True:
    # --- A. Simulación de fluctuaciones ambientales ---
    # Se aplican pequeñas variaciones aleatorias para simular un entorno natural
    humedad_ambiente.valor += (random.randint(1, 2) * random.choice([1, -1]))
    co2.valor += (random.randint(0, 100) * random.choice([1, -1]))
    temperatura_ambiente.valor += (1 * random.choice([1, -1]))
    radiacion_solar.valor += (random.randint(0, 5000) * random.choice([1, -1]))
    humedad_suelo.valor += (random.randint(1, 2) * random.choice([1, -1]))
    pH_agua.valor = round(pH_agua.valor + (0.1 * random.choice([1, -1])), 1)
    
    nombres = ["Humedad Amb.", "CO2", "Temp. Amb.", "Radiación", "Humedad Suelo", "pH Agua"]
    valores = [humedad_ambiente, co2, temperatura_ambiente, radiacion_solar, humedad_suelo, pH_agua]
    
    # Límites operativos normales de las variables del invernadero
    limite_inferior = [35, 300,  10, 10000, 20, 4.5]
    limite_superior = [90, 2500, 35, 50000, 85, 7.5]
    
    # --- B. Empaquetado de Datos ---
    # Construcción del diccionario base que se enviará al servidor
    paquete_datos = {}
    estado_general = "OK"
    for i in range(len(valores)):
        sensor = valores[i]
        paquete_datos[nombres[i]] = {
            "valor": sensor.valor,
            "tipo": sensor.tipo
        }
        if sensor.valor < limite_inferior[i] or sensor.valor > limite_superior[i]:
            estado_general = "ALERTA"
    
    carga_util = {
        "token_acceso": "udec_redes_2026", # Nuestra contraseña básica
        "estado": estado_general,
        "sensores": paquete_datos
    }
        
    # --- C. Inyección de Anomalías (Modo Manual) ---
    if tipo == "1":
        print("\nMenú de eventos de crisis:")
        print("0 = Nada | 1/-1 = Humedad | 2/-2 = CO2 | 3/-3 = Temp | 4/-4 = Radiación | 5/-5 = Humedad Suelo | 6/-6 = pH Agua")
        evento = input("Ingrese el código del evento: ")
        
        try:
            evento = int(evento)
            if evento in [1, -1]:
                humedad_ambiente.valor += 100 * evento
            elif evento in [2, -2]:
                co2.valor += 1000 * evento
            elif evento in [3, -3]:
                temperatura_ambiente.valor += 10 * evento
            elif evento in [4, -4]:
                radiacion_solar.valor += 10000 * evento
            elif evento in [5, -5]:
                humedad_suelo.valor += 100 * evento
            elif evento in [6, -6]:
                pH_agua.valor += 1 * evento
        except ValueError:
            print("Entrada no válida. Ignorando evento.")
    
    # --- D. Verificación Local de Umbrales ---
    # Imprime alertas en consola si los valores salen de los rangos seguros
    for i in range(len(valores)):
        sensor = valores[i]
        if sensor.valor < limite_inferior[i]:
            print(f"ALERTA: {nombres[i]} fuera de rango inferior: {sensor.valor} {sensor.tipo}")
        elif sensor.valor > limite_superior[i]:
            print(f"ALERTA: {nombres[i]} fuera de rango superior: {sensor.valor} {sensor.tipo}")
            
    # --- E. Transmisión HTTP ---
    # Codificación a formato JSON y conversión a bytes para transmisión por red
    
    mensaje_json = json.dumps(carga_util)
    datos_en_bytes = mensaje_json.encode('utf-8')

    # Destino: Servidor central en la máquina virtual Ubuntu
    url = "https://192.168.1.12:5006/datos"

    # Estructuración de la petición HTTP POST
    peticion = urllib.request.Request(url, data=datos_en_bytes, method='POST')
    peticion.add_header('Content-Type', 'application/json')
    
    try:

        contexto_seguro = ssl._create_unverified_context()

        # Ejecución del envío
        respuesta = urllib.request.urlopen(peticion, context=contexto_seguro)
        if respuesta.status == 200:
            print("Datos enviados con éxito vía HTTPS.")
        else:
            print(f"El servidor respondió con código: {respuesta.status}")
            
    except urllib.error.URLError as e:
        # Manejo de fallos: evita que el nodo se detenga si el servidor no responde
        print(f"Fallo de red - No se pudo conectar con el servidor: {e.reason}")
        
    # Imprimir estado actual en consola local
    print("-" * 30)
    for i in range(len(valores)):
        sensor = valores[i]
        print(f"{nombres[i]}: {sensor.valor} {sensor.tipo}")
    print("-" * 30)
        
    # Pausa de 1 segundo antes de la siguiente muestra
    time.sleep(1)