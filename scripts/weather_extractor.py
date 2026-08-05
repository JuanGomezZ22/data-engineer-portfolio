import requests
import json
import os
from pathlib import Path

RAIZ_PROYECTO = Path(__file__).resolve().parent.parent


class WeatherExtractor:
    URL_BASE = "https://archive-api.open-meteo.com/v1/archive"

    def __init__(self, ciudades: dict, fecha_inicio: str, fecha_fin: str, carpeta_salida: str = None):
        self.ciudades = ciudades
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.carpeta_salida = Path(carpeta_salida) if carpeta_salida else RAIZ_PROYECTO / "data" / "raw"

    def extraer_ciudad(self, lat: float, lon: float) -> dict:
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": self.fecha_inicio,
            "end_date": self.fecha_fin,
            "daily": "precipitation_sum,temperature_2m_max,temperature_2m_min",
            "timezone": "America/Lima",
        }
        respuesta = requests.get(self.URL_BASE, params=params)
        respuesta.raise_for_status()
        return respuesta.json()

    def guardar(self, nombre: str, datos: dict) -> str:
        self.carpeta_salida.mkdir(parents=True, exist_ok=True)
        ruta = self.carpeta_salida / f"clima_{nombre}.json"
        with open(ruta, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=2)
        return str(ruta)

    def ejecutar(self) -> None:
        for nombre, coords in self.ciudades.items():
            print(f"Extrayendo {nombre}...")
            datos = self.extraer_ciudad(coords["lat"], coords["lon"])
            ruta = self.guardar(nombre, datos)
            print(f"  -> Guardado en {ruta}")