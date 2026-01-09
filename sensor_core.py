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
            "masa_g": 0.0,      # Para las gráficas (numérico)
            "masa_str": "0.00"  # Para el CSV (texto exacto)
        }
        self.running = True
        self.lock = threading.Lock()

    def _mqtt_on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            with self.lock:
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
                            # Ejemplo entrada: "0.557 g" -> "0.557"
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
            return self.data.copy()

    def stop(self):
        self.running = False
