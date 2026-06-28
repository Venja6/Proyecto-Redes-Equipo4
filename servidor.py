import socket
import json

TCP_IP = "127.0.0.1"
TCP_PORT = 5006

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((TCP_IP, TCP_PORT))
sock.listen(1)

print(f"Servidor TCP a la escucha en el puerto {TCP_PORT}...")
conexion, addr = sock.accept()
print(f"Conexión establecida desde: {addr}")

# Creamos un archivo virtual para leer de forma segura línea por línea (\n)
buffer_lectura = conexion.makefile('r', encoding='utf-8')

while True:
    try:
        # Lee hasta encontrar un salto de línea '\n'
        linea = buffer_lectura.readline()
        if not linea: 
            print("El cliente cerró la conexión.")
            break
        
        # Reconstruimos el JSON a diccionario de Python
        datos_recibidos = json.loads(linea)
        
        print("\n--- NUEVA LECTURA RECIBIDA ---")
        # Iteramos sobre el diccionario para mostrar el valor y el tipo
        for sensor, info in datos_recibidos.items():
            valor = info["valor"]
            tipo = info["tipo"]
            print(f"-> {sensor}: {valor} {tipo}")
            
    except Exception as e:
        print(f"Error procesando datos: {e}")
        break

conexion.close()
sock.close()