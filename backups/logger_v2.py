
import csv
import time
import os
from datetime import datetime
from sensor_core import SensorManager

# Nombre de la carpeta donde se guardarán los archivos
CARPETA_SALIDA = "Recolecciones"

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

def ensure_directory_exists():
    """Crea la carpeta de recolecciones si no existe"""
    if not os.path.exists(CARPETA_SALIDA):
        try:
            os.makedirs(CARPETA_SALIDA)
            print(f"Carpeta '{CARPETA_SALIDA}' creada exitosamente.")
        except OSError as e:
            print(f"Error al crear directorio: {e}")

def run_logger():
    # Asegurar que la carpeta existe antes de empezar
    ensure_directory_exists()

    print("Iniciando conexión con sensores (MQTT + Serial)...")
    manager = SensorManager()
    manager.start()
    time.sleep(1) # Espera técnica para sincronizar hilos

    while True:
        print("\n" + "="*50)
        print("   CONFIGURACIÓN DE NUEVA CAPTURA")
        print("="*50)
        
        # 1. Solicitar datos al usuario
        nombre_muestra = get_input("Nombre de la muestra", "Muestra_Test")
        # Limpiamos espacios en los nombres para evitar errores en el archivo
        nombre_muestra = nombre_muestra.replace(" ", "_")
        
        recolector = get_input("Nombre del recolector", "Operador")
        recolector = recolector.replace(" ", "_")
        
        try:
            intervalo = float(get_input("Intervalo de captura (segundos)", "1.0"))
        except ValueError:
            print("Valor inválido, usando 1.0 segundos.")
            intervalo = 1.0

        duration_sec = get_duration_seconds()
        
        # 2. Generar nombre de archivo según estructura solicitada:
        # "NombreMuestra_Recolector_Fecha.csv"
        # Usamos fecha y hora en el nombre para evitar sobrescribir archivos del mismo día
        fecha_archivo = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{nombre_muestra}_{recolector}_{fecha_archivo}.csv"
        
        # Ruta completa (Carpeta + Archivo)
        filepath = os.path.join(CARPETA_SALIDA, filename)
        
        # 3. Definir Encabezados (Headers) del CSV
        headers = [
            "Fecha_Sistema",    # Fecha legible (YYYY-MM-DD)
            "Hora_Sistema",     # Hora legible (HH:MM:SS)
            "Timestamp_MS",     # El valor original del JSON (Milisegundos)
            "Muestra", 
            "Recolector",
            "Temp1_C", 
            "Hum1_RH", 
            "Temp2_C", 
            "Hum2_RH", 
            "Radiacion_W_m2", 
            "Termopar1_C", 
            "Termopar2_C", 
            "Fan1", 
            "Fan2", 
            "Fan3", 
            "Masa_g"
        ]

        print(f"\nIniciando captura en: {filepath}")
        if duration_sec == -1:
            print("MODO INDEFINIDO: Presiona Ctrl+C para finalizar la captura.")
        else:
            print(f"Duración programada: {duration_sec} segundos.")

        start_time = time.time()
        
        try:
            # Abrimos el archivo en la ruta específica
            with open(filepath, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                
                while True:
                    # Chequeo de tiempo
                    elapsed = time.time() - start_time
                    if duration_sec != -1 and elapsed >= duration_sec:
                        print("\nTiempo de captura finalizado.")
                        break

                    # Obtener datos actuales
                    d = manager.get_data()
                    
                    # Obtener fecha y hora del sistema por separado
                    now = datetime.now()
                    fecha_sys = now.strftime("%Y-%m-%d")
                    hora_sys = now.strftime("%H:%M:%S")
                    
                    row = [
                        fecha_sys,          # Fecha Sistema
                        hora_sys,           # Hora Sistema
                        d['timestamp_ms'],  # Dato original del MQTT
                        nombre_muestra, 
                        recolector,
                        d['temperatura1_C'], 
                        d['humedad1_RH'],
                        d['temperatura2_C'], 
                        d['humedad2_RH'],
                        d['radiacion_W_m2'], 
                        d['termopar1_C'], 
                        d['termopar2_C'],
                        d['ventiladores'][0], 
                        d['ventiladores'][1], 
                        d['ventiladores'][2],
                        d['masa_g']
                    ]
                    
                    writer.writerow(row)
                    file.flush() # Guardado seguro
                    
                    # Feedback visual
                    if duration_sec == -1:
                        print(f"\rCapturando... {int(elapsed)}s | Masa: {d['masa_g']}g", end="")
                    else:
                        pct = (elapsed / duration_sec) * 100
                        print(f"\rProgreso: {pct:.1f}% | Registros: {int(elapsed/intervalo)}", end="")

                    time.sleep(intervalo)

        except KeyboardInterrupt:
            print("\n\nCaptura detenida por el usuario (Ctrl+C).")
        except IOError as e:
            print(f"\nError de entrada/salida (¿Permisos?): {e}")
        
        print(f"\nArchivo guardado exitosamente en: {filepath}")
        
        # Preguntar si continuar
        again = input("\n¿Realizar nueva captura? (s/n): ").lower()
        if again != 's':
            break

    manager.stop()
    print("Programa finalizado.")

if __name__ == "__main__":
    run_logger()
