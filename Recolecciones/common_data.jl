# common_data.jl
using DataFrames, CSV, Dates

function cargar_y_limpiar_csv(ruta_archivo)
    # 1. Cargar ignorando errores leves iniciales, todo como string para limpiar
    df = CSV.read(ruta_archivo, DataFrame; types=String)

    # 2. Función auxiliar para limpiar números sucios (ej: ".98   0.799")
    function parse_float_seguro(val)
        try
            # Si viene vacío o missing
            if ismissing(val) || val == ""; return NaN; end
            # Tomar el último valor si hay espacios (ej. errores de buffer)
            cleaned = split(strip(val))[end] 
            return parse(Float64, cleaned)
        catch
            return NaN
        end
    end

    # 3. Convertir columnas numéricas
    cols_numericas = ["Temp1_C", "Hum1_RH", "Temp2_C", "Hum2_RH", "Radiacion_W_m2",
                      "Termopar1_C", "Termopar2_C", "Termopar3_C", "Termopar4_C", 
                      "Termopar5_C", "Termopar6_C", "Masa_g"]
    
    for col in cols_numericas
        if col in names(df)
            df[!, col] = map(parse_float_seguro, df[!, col])
        end
    end

    # 4. Crear columna DateTime real
    # Asumimos formato AAAA-MM-DD y HH:MM:SS
    df.Datetime = DateTime.(string.(df.Fecha_Sistema, " ", df.Hora_Sistema), "yyyy-mm-dd HH:MM:SS")
    
    return df
end