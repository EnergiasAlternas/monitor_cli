import threading
import json
import time
import serial
import paho.mqtt.client as mqtt

# Configuración
MQTT_BROKER = "localhost"
MQTT_TOPIC = "secador/datos"
SERIAL_PORT = "/dev/ttyUSB0"
SERIAL_BAUD = 9600

class SensorManager:
    def __init__(self):
        # Se actualizaron las claves para coincidir con el nuevo JSON del MQTT
        self.data = {
            "timestamp_ms": 0,
            "temp1_C": 0.0,             # Antes temperatura1_C
            "humedad1_RH": 0.0,
            "temperatura2_C": 0.0,
            "humedad2_RH": 0.0,
            "radiacion_W_m2": 0.0,
            "termopares_C": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], # Lista en lugar de variables sueltas
            "ventiladores": [False, False, False],
            "masa_g": 0.0,      # Mantenemos esto para el Serial (numérico)
            "masa_str": "0.00"  # Mantenemos esto para el Serial (texto exacto)
        }
        self.running = True
        self.lock = threading.Lock()

    def _mqtt_on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            with self.lock:
                # Actualiza solo si la clave existe en nuestro diccionario de datos
                for key, value in payload.items():
                    if key in self.data:
                        self.data[key] = value
        except json.JSONDecodeError:
            pass

    def _start_mqtt(self):
        client = mqtt.Client()
        client.on_message = self._mqtt_on_message
        try:
            client.connect(MQTT_BROKER, 1883, 60)
            client.subscribe(MQTT_TOPIC)
            client.loop_start()
        except Exception:
            pass

    def _start_serial(self):
        while self.running:
            try:
                with serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=1) as ser:
                    while self.running:
                        # Leemos la línea tal cual
                        raw_line = ser.readline().decode('utf-8', errors='ignore').strip()
                        if raw_line:
                            # Limpiamos solo la unidad 'g' o espacios, pero mantenemos el punto decimal
                            val_str = raw_line.lower().replace('g', '').strip()
                            
                            with self.lock:
                                # 1. Guardamos la versión EXACTA como texto para el CSV
                                self.data["masa_str"] = val_str
                                
                                # 2. Intentamos convertir a float solo para el monitor (gráficas)
                                try:
                                    # Reemplazamos coma por punto por si la balanza envía comas
                                    val_float = float(val_str.replace(',', '.'))
                                    self.data["masa_g"] = val_float
                                except ValueError:
                                    pass # Si falla la conversión, mantenemos el último valor válido
            except Exception:
                time.sleep(1)

    def start(self):
        self._start_mqtt()
        serial_thread = threading.Thread(target=self._start_serial, daemon=True)
        serial_thread.start()

    def get_data(self):
        with self.lock:
            # Devuelve una copia para evitar condiciones de carrera al leer
            return self.data.copy()

    def stop(self):
        self.running = False
