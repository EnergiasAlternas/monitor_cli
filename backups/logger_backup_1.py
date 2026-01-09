
import csv
import time
import os
from datetime import datetime, timedelta
from sensor_core import SensorManager

def get_input(prompt, default=None):
    """Helper para inputs con valor por defecto"""
    text = f"{prompt}"
    if default:
        text += f" [{default}]"
    text += ": "
    val = input(text).strip()
    return val if val else default

def get_duration_seconds():
    print("\nSeleccione tiempo de captura:")
    print("1. 1 minuto")
    print("2. 5 minutos")
    print("3. 1 hora")
    print("4. 3 horas")
    print("5. Indefinido (Detener manualmente)")
    
    opcion = input("Opción (1-5): ").strip()
    mapping = {
        "1": 60,
        "2": 300,
        "3": 3600,
        "4": 10800,
        "5": -1 # Indefinido
    }
    return mapping.get(opcion, 60) # Default 1 min

def run_logger():
    # Iniciamos el gestor de sensores
    print("Iniciando conexión con sensores (MQTT + Serial)...")
    manager = SensorManager()
    manager.start()
    time.sleep(1) # Esperar un poco a que lleguen datos

    while True:
        print("\n" + "="*40)
        print("   CONFIGURACIÓN DE NUEVA CAPTURA")
        print("="*40)
        
        nombre_muestra = get_input("Nombre de la muestra", f"Muestra_{int(time.time())}")
        recolector = get_input("Nombre del recolector", "Admin")
        
        try:
            intervalo = float(get_input("Intervalo de captura (segundos)", "1.0"))
        except ValueError:
            print("Valor inválido, usando 1.0 segundos.")
            intervalo = 1.0

        duration_sec = get_duration_seconds()
        
        # Preparar archivo CSV
        filename = f"{nombre_muestra}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Headers del CSV
        headers = [
            "Timestamp_ISO", "Timestamp_MS", "Muestra", "Recolector",
            "Temp1_C", "Hum1_RH", "Temp2_C", "Hum2_RH", 
            "Radiacion_W_m2", "Termopar1_C", "Termopar2_C", 
            "Fan1", "Fan2", "Fan3", "Masa_g"
        ]

        print(f"\nIniciando captura en '{filename}'...")
        if duration_sec == -1:
            print("MODO INDEFINIDO: Presiona Ctrl+C para finalizar la captura.")
        else:
            print(f"Duración programada: {duration_sec} segundos.")

        start_time = time.time()
        try:
            with open(filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                
                while True:
                    # Chequeo de tiempo (si no es indefinido)
                    elapsed = time.time() - start_time
                    if duration_sec != -1 and elapsed >= duration_sec:
                        print("\nTiempo de captura finalizado.")
                        break

                    # Obtener datos
                    d = manager.get_data()
                    now_iso = datetime.now().isoformat()
                    
                    row = [
                        now_iso, d['timestamp_ms'], nombre_muestra, recolector,
                        d['temperatura1_C'], d['humedad1_RH'],
                        d['temperatura2_C'], d['humedad2_RH'],
                        d['radiacion_W_m2'], d['termopar1_C'], d['termopar2_C'],
                        d['ventiladores'][0], d['ventiladores'][1], d['ventiladores'][2],
                        d['masa_g']
                    ]
                    
                    writer.writerow(row)
                    file.flush() # Asegurar escritura en disco
                    
                    # Feedback visual simple
                    if duration_sec == -1:
                        print(f"\rCapturando... {int(elapsed)}s (Ctrl+C para parar)", end="")
                    else:
                        pct = (elapsed / duration_sec) * 100
                        print(f"\rProgreso: {pct:.1f}% | Registros: {int(elapsed/intervalo)}", end="")

                    time.sleep(intervalo)

        except KeyboardInterrupt:
            print("\n\nCaptura detenida por el usuario.")
        
        print(f"\nArchivo guardado: {filename}")
        
        # Preguntar si continuar
        again = input("\n¿Realizar nueva captura? (s/n): ").lower()
        if again != 's':
            break

    manager.stop()
    print("Programa finalizado.")

if __name__ == "__main__":
    run_logger()
