import requests
import json
import os
from datetime import date

CIUDADES = {
    "piura": {"lat": -5.19, "lon": -80.63},
    "tumbes": {"lat": -3.57, "lon": -80.45},
    "chiclayo": {"lat": -6.77, "lon": -79.84},
    "trujillo": {"lat": -8.11, "lon": -79.02},
    "lima": {"lat": -12.05, "lon": -77.04},
}

FECHA_INICIO = "2010-01-01"
FECHA_FIN = date.today().isoformat()
URL_BASE = "https://archive-api.open-meteo.com/v1/archive"
CARPETA_SALIDA = "data/raw"

def extraer_datos_ciudad(nombre, lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": FECHA_INICIO,
        "end_date": FECHA_FIN,
        "daily": "precipitation_sum,temperature_2m_max,temperature_2m_min",
        "timezone": "America/Lima",
    }
    respuesta = requests.get(URL_BASE, params=params)
    respuesta.raise_for_status()
    return respuesta.json()

def guardar_json(nombre, datos):
    os.makedirs(CARPETA_SALIDA, exist_ok=True)
    ruta = os.path.join(CARPETA_SALIDA, f"clima_{nombre}.json")
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)
    print(f"Guardado: {ruta}")

if __name__ == "__main__":
    for nombre, coords in CIUDADES.items():
        print(f"Extrayendo datos de {nombre}...")
        datos = extraer_datos_ciudad(nombre, coords["lat"], coords["lon"])
        guardar_json(nombre, datos)