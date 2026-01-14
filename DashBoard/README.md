# ☀️ Fasbit Solar Monitor

Este proyecto es una herramienta de análisis y visualización de datos diseñada para monitorear el rendimiento de **colectores solares**. Está escrito en **Julia** para aprovechar su alta velocidad de procesamiento y capacidades gráficas.

El sistema es capaz de leer archivos CSV generados por el sistema de recolección, limpiar errores de transmisión en los datos y presentar la información en dos modalidades:

1.  **🖥️ CLI (Terminal):** Interfaz ligera estilo *btop* para servidores o acceso rápido.
2.  **📈 GUI (Gráfica):** Interfaz interactiva completa con zoom y exploración detallada.

---

## 🚀 Características

*   **Limpieza Automática de Datos:** Maneja errores de formato en el CSV (ej. espacios extra, líneas corruptas o saltos en la columna de Masa).
*   **Fusión de Fecha/Hora:** Combina automáticamente las columnas `Fecha_Sistema` y `Hora_Sistema`.
*   **Modo TUI (Terminal User Interface):**
    *   Gráficos renderizados con caracteres Unicode/Braille.
    *   Panel de estadísticas resumen.
    *   Navegación por menús en consola.
*   **Modo GUI (Graphical User Interface):**
    *   Renderizado acelerado por GPU usando `GLMakie`.
    *   Gráficos interactivos (Zoom, Pan, Inspección de datos).
    *   Ejes sincronizados para correlacionar Temperatura vs Masa/Humedad.

---

## 📋 Requisitos Previos

*   **Julia Lang**: Versión 1.8 o superior. [Descargar Julia](https://julialang.org/downloads/).
*   **Archivos de Datos**: Archivos `.csv` en el directorio raíz del proyecto con la estructura esperada (columnas: `Temp1_C`, `Hum1_RH`, `Masa_g`, `TermoparX_C`, etc.).

---

## 🛠️ Instalación

1.  **Clona o descarga** este repositorio en tu carpeta de trabajo.
2.  Abre una terminal en la carpeta del proyecto e inicia Julia:
    ```bash
    julia
    ```
3.  Instala las dependencias necesarias copiando y pegando lo siguiente en la consola de Julia:

    ```julia
    using Pkg
    Pkg.add([
        "DataFrames", 
        "CSV", 
        "Dates", 
        "Statistics",
        "UnicodePlots", 
        "Term", 
        "GLMakie", 
        "REPL"
    ])
    ```

---

## 📂 Estructura de Archivos

Asegúrate de tener los siguientes archivos en la misma carpeta:

*   `common_data.jl`: Módulo lógico para cargar y limpiar los datos CSV.
*   `monitor_tui.jl`: Script para la versión de Terminal.
*   `monitor_gui.jl`: Script para la versión Gráfica.
*   `*.csv`: Tus archivos de datos (ej: `Fasbit_Areli_2026-01-13.csv`).

---

## ▶️ Ejecución

### Opción 1: Interfaz de Terminal (Ligera)
Ideal para verificaciones rápidas o conexiones remotas (SSH).

```bash
julia monitor_tui.jl