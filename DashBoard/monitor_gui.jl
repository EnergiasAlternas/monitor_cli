using GLMakie
using DataFrames
using Dates

# Incluimos la lógica de carga
include("common_data.jl")

function lanzar_gui()
    # Configuración de la ventana
    GLMakie.activate!()
    fig = Figure(size = (1200, 800), title = "Fasbit Solar Analysis", theme = theme_dark())

    # --- Layout ---
    # Barra lateral para controles
    grid_controls = fig[1, 1] = GridLayout()
    # Área principal para gráficas
    grid_plots = fig[1, 2] = GridLayout()
    
    # Ajustar ancho de columna izquierda
    colsize!(fig.layout, 1, Fixed(250))

    # --- Controles ---
    archivos = filter(x -> endswith(x, ".csv"), readdir())
    if isempty(archivos)
        push!(archivos, "No csv found")
    end

    lbl_header = Label(grid_controls[1, 1], "🗂️ Archivos", fontsize=20, font=:bold)
    menu_archivos = Menu(grid_controls[2, 1], options = archivos, tellwidth=true)
    
    lbl_stats = Label(grid_controls[3, 1], "Estadísticas:\nSeleccione archivo...", justification=:left)

    # --- Observables (Datos reactivos) ---
    # Usamos Observables para actualizar los datos sin redibujar toda la ventana
    time_obs = Observable(DateTime[])
    temp1_obs = Observable(Float64[])
    termopar1_obs = Observable(Float64[])
    termopar2_obs = Observable(Float64[])
    hum_obs = Observable(Float64[])
    masa_obs = Observable(Float64[])
    
    # --- Gráficas ---
    # 1. Gráfica Principal (Temperaturas)
    ax_temp = Axis(grid_plots[1, 1], title="Temperaturas (°C)", xlabel="Tiempo", ylabel="°C")
    lines!(ax_temp, time_obs, temp1_obs, label="Temp Ambiente", color=:cyan, linewidth=2)
    lines!(ax_temp, time_obs, termopar1_obs, label="Termopar 1", color=:orange)
    lines!(ax_temp, time_obs, termopar2_obs, label="Termopar 2", color=:red)
    axislegend(ax_temp)

    # 2. Gráfica Secundaria (Masa y Humedad) - Doble Eje Y
    ax_masa = Axis(grid_plots[2, 1], title="Masa y Humedad", xlabel="Tiempo", ylabel="Masa (g)")
    ax_hum = Axis(grid_plots[2, 1], ylabel="Humedad (%)", yaxisposition=:right)
    hidespines!(ax_hum)
    hidexdecorations!(ax_hum)
    
    lines!(ax_masa, time_obs, masa_obs, color=:green, label="Masa")
    lines!(ax_hum, time_obs, hum_obs, color=:blue, linestyle=:dash, label="Humedad")
    
    # Linkear eje X para zoom sincronizado
    linkxaxes!(ax_temp, ax_masa)

    # --- Lógica de Interacción ---
    on(menu_archivos.selection) do archivo
        try
            df = cargar_y_limpiar_csv(archivo)
            
            # Actualizar datos
            time_obs[] = df.Datetime
            temp1_obs[] = df.Temp1_C
            termopar1_obs[] = df.Termopar1_C
            termopar2_obs[] = df.Termopar2_C
            hum_obs[] = df.Hum1_RH
            masa_obs[] = df.Masa_g
            
            # Resetear vista para encajar nuevos datos
            reset_limits!(ax_temp)
            reset_limits!(ax_masa)
            reset_limits!(ax_hum)

            # Actualizar stats
            lbl_stats.text = """
            Archivo: $archivo
            Muestras: $(nrow(df))
            
            Promedios:
            Temp Amb: $(round(mean(filter(!isnan, df.Temp1_C)), digits=1)) °C
            Masa: $(round(mean(filter(!isnan, df.Masa_g)), digits=3)) g
            """
        catch e
            println("Error cargando archivo: $e")
        end
    end

    # Seleccionar el primer archivo automáticamente si existe
    if !isempty(archivos)
        menu_archivos.i_selected = 1
    end

    display(fig)
    # Mantener ventana abierta si se ejecuta como script
    wait(display(fig))
end

lanzar_gui()