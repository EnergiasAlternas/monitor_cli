import threading
import json
import time
import serial
import paho.mqtt.client as mqtt
from datetime import datetime

# Configuración por defecto
MQTT_BROKER = "localhost" # O la IP del broker si es externo
MQTT_TOPIC = "secador/datos"
SERIAL_PORT = "/dev/ttyUSB0"
SERIAL_BAUD = 9600

class SensorManager:
    def __init__(self):
        self.data = {
            "timestamp_ms": 0,
            "temperatura1_C": 0.0,
            "humedad1_RH": 0.0,
            "temperatura2_C": 0.0,
            "humedad2_RH": 0.0,
            "radiacion_W_m2": 0.0,
            "termopar1_C": 0.0,
            "termopar2_C": 0.0,
            "ventiladores": [False, False, False],
            "masa_g": 0.0  # Valor de la balanza
        }
        self.running = True
        self.lock = threading.Lock() # Para evitar conflictos de lectura/escritura

    def _mqtt_on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            with self.lock:
                # Actualizamos todos los campos excepto la masa (que viene por serial)
                for key, value in payload.items():
                    if key in self.data:
                        self.data[key] = value
        except json.JSONDecodeError:
            pass # Ignorar paquetes corruptos

    def _start_mqtt(self):
        client = mqtt.Client()
        client.on_message = self._mqtt_on_message
        try:
            client.connect(MQTT_BROKER, 1883, 60)
            client.subscribe(MQTT_TOPIC)
            client.loop_start()
        except Exception as e:
            print(f"Error MQTT: {e}")

    def _start_serial(self):
        while self.running:
            try:
                with serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=1) as ser:
                    while self.running:
                        line = ser.readline().decode('utf-8').strip()
                        if line:
                            try:
                                # Asumimos que la balanza envía solo el número o texto parseable
                                # Ajusta el split/replace según el formato exacto de tu balanza
                                val = float(line.replace('g', '').strip())
                                with self.lock:
                                    self.data["masa_g"] = val
                            except ValueError:
                                pass # Ignorar líneas que no son números
            except serial.SerialException:
                # Si la balanza no está conectada, reintentar cada 2 segs sin romper el programa
                time.sleep(2)
            except Exception:
                time.sleep(1)

    def start(self):
        # Iniciar hilo MQTT
        self._start_mqtt()
        
        # Iniciar hilo Serial
        serial_thread = threading.Thread(target=self._start_serial, daemon=True)
        serial_thread.start()

    def get_data(self):
        """Retorna una copia segura de los datos actuales"""
        with self.lock:
            return self.data.copy()

    def stop(self):
        self.running = False
