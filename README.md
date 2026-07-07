# Proyecto-Redes-Equipo4
__Integrantes:__

Luis Martinez Neira<br>
2023427985

Felipe Tilleria Morales<br>
2023425915

Benjamín Díaz Ulloa<br> 
2023451053

Diego Gutiérrez Mendoza<br>
2020405271

# Sobre el proyecto

Consiste en un entorno que representa un invernadero y las variables ambientales provenientes de los sensores simulados en su interior. El objetivo principal es enviar, recibir y analizar estas variables mediante un sistema de comunicación online basado en el protocolo HTTPS para monitorear la situación de forma remota.

El sistema se compone de dos componentes principales implementados en Python:

* __Cliente Edge (invernadero_cliente.py):__ Actúa como un nodo simulado que recopila datos y genera fluctuaciones ambientales. Envía datos periódicamente y tiene la capacidad de recibir comandos de reconfiguración si los valores caen en rangos críticos.  

* __Servidor Central (servidor.py):__ Servidor Flask que recibe, valida y centraliza la información proveniente de los clientes. Expone un dashboard interactivo mediante una interfaz web para visualizar el estado del invernadero y enviar órdenes de corrección.  

# Requisitos Previos

Se necesita del lenguaje de programacion python y de Oracle virtualbox para crear una MV que contenga la imagen de Ubuntu.

# Instalación y Configuración de la MV

Asegúrese de tener las dependencias de OpenSSL instaladas para evitar fallos con el certificado HTTPS autofirmado:
```bash
sudo apt update
sudo apt install python3-openssl
```
Tambien se debe de tener instalado flask en donde se ejecutara el el servidor.
```bash
pip install Flask
```

El servidor expone su API en el puerto 5006 a través del protocolo TCP. Si el nodo cliente (invernadero) arroja errores de conexión o tiempos de espera agotados, verifique que el firewall de la máquina virtual permita el tráfico entrante ejecutando:
```bash
sudo ufw allow 5006/tcp
```
# Ejecución

__1. Iniciar el Servidor:__
Ejecute el servidor central desde la MV. Este levantará la interfaz y comenzará a escuchar peticiones HTTPS. __Tambien debe de asegurarse que la MV tenga adaptador puente en su configuracion de red__.
```bash
  python servidor.py
```
El panel de control estará disponible en su navegador accediendo a: https://<IP_DEL_SERVIDOR>:5006/

__2. Iniciar el Cliente:__ En la máquina host o terminal que actúa como invernadero, inicie la simulación:

```bash
  python invernadero_cliente.py
```
El script solicitará por consola la dirección IP del servidor y el modo de operación (0 = Automático, 1 = Manual para forzar una crisis ambiental).
