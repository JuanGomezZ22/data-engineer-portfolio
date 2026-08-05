import pandas as pd
import json
import os
from pathlib import Path

RAIZ_PROYECTO = Path(__file__).resolve().parent.parent


class WeatherTransformer:
    def __init__(self, carpeta_raw: str = None, carpeta_processed: str = None):
        self.carpeta_raw = Path(carpeta_raw) if carpeta_raw else RAIZ_PROYECTO / "data" / "raw"
        self.carpeta_processed = Path(carpeta_processed) if carpeta_processed else RAIZ_PROYECTO / "data" / "processed"

    def cargar_json(self, nombre_ciudad: str) -> dict:
        ruta = self.carpeta_raw / f"clima_{nombre_ciudad}.json"
        with open(ruta, "r", encoding="utf-8") as archivo:
            return json.load(archivo)

    def json_a_dataframe(self, datos: dict, nombre_ciudad: str) -> pd.DataFrame:
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

    def limpiar(self, df: pd.DataFrame) -> pd.DataFrame:
        df["fecha"] = pd.to_datetime(df["fecha"])
        df["precipitacion_mm"] = df["precipitacion_mm"].fillna(0)
        return df.dropna(subset=["temp_max", "temp_min"])

    def ejecutar(self, ciudades: list[str]) -> pd.DataFrame:
        dataframes = [self.limpiar(self.json_a_dataframe(self.cargar_json(c), c)) for c in ciudades]
        df_maestro = pd.concat(dataframes, ignore_index=True)

        self.carpeta_processed.mkdir(parents=True, exist_ok=True)
        ruta_salida = self.carpeta_processed / "clima_el_nino_maestro.csv"
        df_maestro.to_csv(ruta_salida, index=False)
        print(f"Guardado en: {ruta_salida}")
        return df_maestro