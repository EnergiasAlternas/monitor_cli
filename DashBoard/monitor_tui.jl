using Term
using UnicodePlots
using REPL.TerminalMenus
using Dates
using Statistics

# Incluimos la lógica de carga (copia la función de arriba aquí o usa include)
include("common_data.jl") 

function menu_principal()
    # Buscar archivos CSV en la carpeta actual
    archivos = filter(x -> endswith(x, ".csv"), readdir())
    
    if isempty(archivos)
        println(@red "No se encontraron archivos CSV en este directorio.")
        return
    end

    # Menú interactivo de selección
    menu = RadioMenu(archivos, pagesize=10)
    choice = request("Selecciona un archivo para analizar:", menu)

    if choice != -1
        archivo_selec = archivos[choice]
        mostrar_dashboard(archivo_selec)
    else
        println("Salida.")
    end
end

function mostrar_dashboard(archivo)
    df = cargar_y_limpiar_csv(archivo)
    
    # Limpiar pantalla
    print("\033c")

    # --- Generación de Gráficos ---
    
    # 1. Temperaturas Termopares (Series múltiples)
    plt_termopares = lineplot(df.Datetime, df.Termopar1_C, title="Termopares (1-3)", name="T1", height=10, width=60)
    lineplot!(plt_termopares, df.Datetime, df.Termopar2_C, name="T2")
    lineplot!(plt_termopares, df.Datetime, df.Termopar3_C, name="T3")

    # 2. Humedad
    plt_humedad = lineplot(df.Datetime, df.Hum1_RH, title="Humedad Relativa %", color=:cyan, height=5, width=60)
    
    # 3. Masa
    plt_masa = lineplot(df.Datetime, df.Masa_g, title="Masa (g)", color=:green, height=5, width=60)

    # --- Panel de Estadísticas (Estilo btop) ---
    t_prom = round(mean(filter(!isnan, df.Temp1_C)), digits=2)
    h_prom = round(mean(filter(!isnan, df.Hum1_RH)), digits=2)
    m_max = round(maximum(filter(!isnan, df.Masa_g)), digits=3)
    registros = nrow(df)
    
    info_panel = Panel(
        "{bold white}Archivo:{/bold white} $archivo\n" *
        "{bold yellow}Registros:{/bold yellow} $registros\n" *
        "{bold red}Temp Prom:{/bold red} $t_prom °C\n" *
        "{bold cyan}Hum Prom:{/bold cyan} $h_prom %\n" *
        "{bold green}Masa Max:{/bold green} $m_max g";
        title="Resumen", fit=true, style="blue"
    )

    # --- Layout con Term.jl ---
    # Convertimos los plots a string para meterlos en paneles
    p1 = Panel(string(plt_termopares), title="Perfil Térmico", style="red", fit=true)
    p2 = Panel(string(plt_humedad) * "\n" * string(plt_masa), title="Ambiente y Masa", style="green", fit=true)

    # Renderizado final
    print(Panel(
        grid([
            info_panel;
            p1 p2
        ]),
        title="Fasbit Solar Monitor - CLI", style="bold white", fit=true
    ))
    
    println("\nPresiona Enter para volver al menú...")
    readline()
    menu_principal() # Loop
end

# Iniciar
menu_principal()