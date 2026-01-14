using Term
using UnicodePlots
using REPL.TerminalMenus
using Dates
using Statistics

# Incluimos la lógica de carga
include("common_data.jl") 

function menu_principal()
    # Buscar archivos CSV
    archivos = filter(x -> endswith(x, ".csv"), readdir())
    
    if isempty(archivos)
        println(@red "No se encontraron archivos CSV en este directorio.")
        return
    end

    # Limpiar pantalla y mostrar logo simple
    print("\033c")
    println(Panel("{bold orange}Fasbit Solar Monitor{/bold orange}", fit=true, style="orange"))

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

    # --- 1. Calcular Dimensiones de la Terminal ---
    h_term, w_term = displaysize(stdout)

    # Márgenes y reservas:
    # Header: ~8 líneas. Prompt final: ~2 líneas. Bordes: ~4 líneas.
    h_disponible = max(10, h_term - 12) 
    
    # Ancho: Dividimos entre 2 columnas. Restamos ~6 chars por bordes de paneles y padding.
    w_plot = max(20, div(w_term, 2) - 6)

    # Alturas específicas
    h_plot_alto = h_disponible            # Para la columna izquierda (Temperatura)
    h_plot_bajo = div(h_disponible, 2) - 1 # Para la columna derecha dividida (Humedad/Masa)

    # --- 2. Generación de Gráficos Adaptables ---
    
    # Gráfica Izquierda (Alta): Temperaturas
    # Usamos todas las series disponibles
    plt_termopares = lineplot(df.Datetime, df.Termopar1_C, 
        title="Perfil Térmico (ºC)", name="T1", 
        height=h_plot_alto, width=w_plot, margin=0)
    
    lineplot!(plt_termopares, df.Datetime, df.Termopar2_C, name="T2")
    lineplot!(plt_termopares, df.Datetime, df.Termopar3_C, name="T3")
    # Agregamos temperatura ambiente si cabe
    if maximum(df.Temp1_C) > 0
        lineplot!(plt_termopares, df.Datetime, df.Temp1_C, name="Amb", color=:blue)
    end

    # Gráfica Derecha Superior: Humedad
    plt_humedad = lineplot(df.Datetime, df.Hum1_RH, 
        title="Humedad (%)", color=:cyan, 
        height=h_plot_bajo, width=w_plot, margin=0)
    
    # Gráfica Derecha Inferior: Masa
    plt_masa = lineplot(df.Datetime, df.Masa_g, 
        title="Masa (g)", color=:green, 
        height=h_plot_bajo, width=w_plot, margin=0)

    # --- 3. Panel de Estadísticas (Encabezado) ---
    t_prom = round(mean(filter(!isnan, df.Termopar1_C)), digits=2)
    m_max = round(maximum(filter(!isnan, df.Masa_g)), digits=3)
    registros = nrow(df)
    
    # Calculamos duración
    duracion = try
        round(df.Datetime[end] - df.Datetime[1], Dates.Minute)
    catch
        "N/A"
    end
    
    # Creamos el texto del resumen
    txt_resumen = "{bold white}Archivo:{/bold white} $archivo  |  " *
                  "{bold yellow}Regs:{/bold yellow} $registros  |  " *
                  "{bold blue}Duración:{/bold blue} $duracion\n" *
                  "{bold red}T. Prom (T1):{/bold red} $t_prom °C  |  " *
                  "{bold green}Masa Max:{/bold green} $m_max g"

    # Panel de encabezado que ocupa todo el ancho
    info_panel = Panel(
        txt_resumen;
        title="Resumen General", 
        style="blue", 
        width=w_term - 4, # Ancho total menos bordes
        justify=:center,
        fit=false # Forzamos el ancho calculado
    )

    # --- 4. Layout con Paneles ---
    
    # Panel Izquierdo (Gráfica Alta)
    p_izq = Panel(string(plt_termopares), title="Sensores Térmicos", style="red", fit=true)
    
    # Panel Derecho (Dos Gráficas Apiladas)
    # Concatenamos strings para que queden una encima de otra dentro del mismo panel
    content_der = string(plt_humedad) * "\n" * string(plt_masa)
    p_der = Panel(content_der, title="Ambiente y Recolección", style="green", fit=true)

    # Composición Final
    # Info arriba / (Izquierda * Derecha)
    try
        print(info_panel / (p_izq * p_der))
    catch e
        # Fallback por si la terminal es muy estrecha para ponerlos lado a lado
        print(info_panel / p_izq / p_der)
    end
    
    println("\n{dim}Presiona Enter para volver al menú...{/dim}")
    readline()
    menu_principal() 
end

# Iniciar
menu_principal()