#!/bin/bash

# 1. Moverse al directorio del proyecto (CRUCIAL para que encuentre los archivos)
cd /home/alternas/Proyectos/monitor-cli

# 2. Activar el entorno virtual
source .venv/bin/activate

# 3. Ejecutar con uv
# Nota: Si uv no se encuentra, podrías necesitar poner la ruta completa 
# (ej: /home/alternas/.cargo/bin/uv run monitor.py)
uv run logger.py

# 4. Pausa al final (Opcional)
# Esto evita que la ventana se cierre de golpe si hay un error, para que puedas leerlo.
echo "El programa ha finalizado."
read -p "Presiona Enter para cerrar esta ventana..."