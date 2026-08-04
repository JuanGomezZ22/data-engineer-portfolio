import pandas as pd
import json
import os

CARPETA_RAW = "data/raw"
CARPETA_PROCESSED = "data/processed"
CIUDADES = ["piura", "tumbes", "chiclayo", "trujillo", "lima"]

def cargar_json_ciudad(nombre_ciudad):
    ruta = os.path.join(CARPETA_RAW, f"clima_{nombre_ciudad}.json")
    with open(ruta, "r", encoding="utf-8") as archivo:
        datos = json.load(archivo)
    return datos

def json_a_dataframe(datos, nombre_ciudad):
    diario = datos["daily"]
    df = pd.DataFrame({
        "fecha": diario["time"],
        "precipitacion_mm": diario["precipitation_sum"],
        "temp_max": diario["temperature_2m_max"],
        "temp_min": diario["temperature_2m_min"],
    })
    df["ciudad"] = nombre_ciudad
    df["latitud"] = datos["latitude"]
    df["longitud"] = datos["longitude"]
    return df

def limpiar_dataframe(df):
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["precipitacion_mm"] = df["precipitacion_mm"].fillna(0)
    df = df.dropna(subset=["temp_max", "temp_min"])
    return df

if __name__ == "__main__":
    dataframes = []

    for ciudad in CIUDADES:
        print(f"Procesando {ciudad}...")
        datos = cargar_json_ciudad(ciudad)
        df_ciudad = json_a_dataframe(datos, ciudad)
        dataframes.append(df_ciudad)

    df_maestro = pd.concat(dataframes, ignore_index=True)
    df_maestro = limpiar_dataframe(df_maestro)

    print("\n--- Resumen del DataFrame maestro ---")
    print(df_maestro.info())
    print("\nValores nulos por columna:")
    print(df_maestro.isnull().sum())
    print(f"\nTotal de filas: {len(df_maestro)}")

    os.makedirs(CARPETA_PROCESSED, exist_ok=True)
    ruta_salida = os.path.join(CARPETA_PROCESSED, "clima_el_nino_maestro.csv")
    df_maestro.to_csv(ruta_salida, index=False)
    print(f"\nGuardado en: {ruta_salida}")