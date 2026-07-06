from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)

historial_datos = []
# Diccionario para almacenar comandos destinados al nodo Edge (ej: {"sensor_afectado": "accion"})
comandos_pendientes = {} 
MAX_REGISTROS = 30

@app.route('/datos', methods=['POST'])
def recibir_datos():
    try:
        payload = request.get_json()
        
        # Validación del Token de seguridad
        token = payload.get("token_acceso")
        if token != "udec_redes_2026":
            return jsonify({"status": "error", "message": "No autorizado"}), 401
        
        estado_general = payload.get("estado")
        sensores = payload.get("sensores")
        
        # Guardar registro
        registro = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "estado": estado_general,
            "sensores": {},
            "sensor_alerta": None  # Aquí guardaremos cuál está fallando
        }
        
        for nombre, datos_sensor in sensores.items():
            registro["sensores"][nombre] = f"{datos_sensor['valor']} {datos_sensor['tipo']}"
            # Si el estado es ALERTA, intentamos deducir cuál es el sensor fallando 
            # (En un entorno real, el cliente te diría explícitamente cuál está mal)
            if estado_general == "ALERTA" and datos_sensor.get("critico") == True:
                registro["sensor_alerta"] = nombre

        historial_datos.insert(0, registro)
        if len(historial_datos) > MAX_REGISTROS: historial_datos.pop()
            
        # --- RESPUESTA AL CLIENTE EDGE ---
        # Le enviamos al cliente si hay alguna orden de reparación esperándolo
        respuesta = {"status": "success", "message": "Datos procesados"}
        if comandos_pendientes:
            respuesta["comandos"] = comandos_pendientes.copy()
            comandos_pendientes.clear() # Limpiamos los comandos una vez enviados al Edge
            
        return jsonify(respuesta), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --- NUEVA RUTA: Recibir la orden de reparación desde la interfaz web ---
@app.route('/api/solucionar', methods=['POST'])
def enviar_solucion():
    data = request.get_json()
    sensor = data.get("sensor")
    if sensor:
        # Registramos que este sensor debe ser "reseteado" o "corregido"
        comandos_pendientes[sensor] = "CORREGIR_VALOR"
        print(f"\n[COMANDO] Orden de reparación enviada para el sensor: {sensor}\n")
        return jsonify({"status": "ok", "message": f"Solución enviada para {sensor}"}), 200
    return jsonify({"status": "error", "message": "No se especificó el sensor"}), 400


@app.route('/api/historial', methods=['GET'])
def obtener_historial():
    return jsonify(historial_datos)


@app.route('/', methods=['GET'])
def index():
    html_dashboard = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Control de Sensores en Vivo</title>
        <style>
            body { font-family: sans-serif; margin: 30px; background-color: #f4f6f9; color: #333; }
            .badge { padding: 5px 10px; border-radius: 4px; font-weight: bold; font-size: 12px; }
            .badge-ok { background-color: #2ecc71; color: white; }
            /* Botón de Alerta Interactiva */
            .btn-alerta { background-color: #e74c3c; color: white; border: none; padding: 6px 12px; 
                          border-radius: 4px; font-weight: bold; cursor: pointer; transition: 0.2s; }
            .btn-alerta:hover { background-color: #c0392b; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; background: white; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background-color: #34495e; color: white; }
        </style>
    </head>
    <body>
        <h1> Monitoreo y Control en Tiempo Real</h1>
        <table>
            <thead>
                <tr id="headers-tabla">
                    <th>Hora</th>
                    <th>Estado</th>
                </tr>
            </thead>
            <tbody id="cuerpo-tabla"></tbody>
        </table>

        <script>
            let sensoresDetectados = new Set();

            async function arreglarSensor(nombreSensor) {
                if(!confirm(`¿Deseas enviar comando de corrección para: ${nombreSensor}?`)) return;
                
                const response = await fetch('/api/solucionar', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ sensor: nombreSensor })
                });
                const res = await response.json();
                alert(res.message);
            }

            async function actualizarTabla() {
                try {
                    const response = await fetch('/api/historial');
                    const datos = await response.json();
                    if (datos.length === 0) return;

                    datos.forEach(reg => Object.keys(reg.sensores).forEach(s => sensoresDetectados.add(s)));
                    const listaSensores = Array.from(sensoresDetectados);

                    const headerRow = document.getElementById('headers-tabla');
                    headerRow.innerHTML = '<th>Hora</th><th>Estado</th>';
                    listaSensores.forEach(s => headerRow.innerHTML += `<th>${s}</th>`);

                    const cuerpo = document.getElementById('cuerpo-tabla');
                    cuerpo.innerHTML = '';

                    datos.forEach(reg => {
                        // Si está en alerta, convertimos el estado en un BOTÓN dinámico
                        let estadoCelda = `<span class="badge badge-ok">OK</span>`;
                        if(reg.estado === 'ALERTA' && reg.sensor_alerta) {
                            estadoCelda = `<button class="btn-alerta" onclick="arreglarSensor('${reg.sensor_alerta}')">⚠️ Corregir ${reg.sensor_alerta}</button>`;
                        } else if (reg.estado === 'ALERTA') {
                            estadoCelda = `<span class="badge" style="background:#f39c12; color:white;">ALERTA GENERAL</span>`;
                        }

                        let filaHtml = `<tr><td>${reg.timestamp}</td><td>${estadoCelda}</td>`;
                        
                        listaSensores.forEach(sensor => {
                            const valorSensor = reg.sensores[sensor] || '-';
                            // Resaltar en rojo el valor de la celda afectada
                            const estiloCritico = (reg.estado === 'ALERTA' && reg.sensor_alerta === sensor) ? 'style="color:red; font-weight:bold;"' : '';
                            filaHtml += `<td ${estiloCritico}>${valorSensor}</td>`;
                        });
                        
                        filaHtml += '</tr>';
                        cuerpo.innerHTML += filaHtml;
                    });
                } catch (e) { console.error(e); }
            }

            setInterval(actualizarTabla, 2000);
            actualizarTabla();
        </script>
    </body>
    </html>
    """
    return render_template_string(html_dashboard)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=True, ssl_context='adhoc')