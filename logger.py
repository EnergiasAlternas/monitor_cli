
import csv
import time
import os
from datetime import datetime
from sensor_core import SensorManager

CARPETA_SALIDA = "Recolecciones"

def get_input(prompt, default=None):
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
    mapping = {"1": 60, "2": 300, "3": 3600, "4": 10800, "5": -1}
    return mapping.get(opcion, 60)

def ensure_directory_exists():
    if not os.path.exists(CARPETA_SALIDA):
        try:
            os.makedirs(CARPETA_SALIDA)
        except OSError:
            pass

def run_logger():
    ensure_directory_exists()
    print("Iniciando conexión con sensores...")
    manager = SensorManager()
    manager.start()
    time.sleep(1)

    while True:
        print("\n" + "="*50)
        print("   CONFIGURACIÓN DE NUEVA CAPTURA")
        print("="*50)
        
        nombre_muestra = get_input("Nombre de la muestra", "Muestra_Test").replace(" ", "_")
        recolector = get_input("Nombre del recolector", "Operador").replace(" ", "_")
        try:
            intervalo = float(get_input("Intervalo (seg)", "1.0"))
        except ValueError:
            intervalo = 1.0
        
        duration_sec = get_duration_seconds()
        
        fecha_archivo = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{nombre_muestra}_{recolector}_{fecha_archivo}.csv"
        filepath = os.path.join(CARPETA_SALIDA, filename)
        
        headers = [
            "Fecha_Sistema", "Hora_Sistema", "Timestamp_MS", "Muestra", "Recolector",
            "Temp1_C", "Hum1_RH", "Temp2_C", "Hum2_RH", "Radiacion_W_m2", 
            "Termopar1_C", "Termopar2_C", "Fan1", "Fan2", "Fan3", 
            "Masa_g" # Aquí guardaremos el valor crudo
        ]

        print(f"\nIniciando captura en: {filepath}")
        if duration_sec == -1: print("MODO INDEFINIDO: Ctrl+C para parar.")
        
        start_time = time.time()
        
        try:
            with open(filepath, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                
                while True:
                    elapsed = time.time() - start_time
                    if duration_sec != -1 and elapsed >= duration_sec:
                        print("\nTiempo finalizado.")
                        break

                    d = manager.get_data()
                    now = datetime.now()
                    
                    row = [
                        now.strftime("%Y-%m-%d"),
                        now.strftime("%H:%M:%S"),
                        d['timestamp_ms'],
                        nombre_muestra,
                        recolector,
                        d['temperatura1_C'], d['humedad1_RH'],
                        d['temperatura2_C'], d['humedad2_RH'],
                        d['radiacion_W_m2'], d['termopar1_C'], d['termopar2_C'],
                        d['ventiladores'][0], d['ventiladores'][1], d['ventiladores'][2],
                        # CAMBIO IMPORTANTE: Usamos masa_str, no masa_g
                        d['masa_str'] 
                    ]
                    
                    writer.writerow(row)
                    file.flush()
                    
                    # Feedback visual (usamos d['masa_str'] para confirmar que se lee bien)
                    if duration_sec == -1:
                        print(f"\rCapturando... {int(elapsed)}s | Masa: {d['masa_str']}  ", end="")
                    else:
                        pct = (elapsed / duration_sec) * 100
                        print(f"\rProgreso: {pct:.1f}% | Registros: {int(elapsed/intervalo)}", end="")

                    time.sleep(intervalo)

        except KeyboardInterrupt:
            print("\nCaptura detenida (Ctrl+C).")
        
        print(f"\nGuardado en: {filepath}")
        if input("\n¿Nueva captura? (s/n): ").lower() != 's':
            break

    manager.stop()
    print("Fin.")

if __name__ == "__main__":
    run_logger()
