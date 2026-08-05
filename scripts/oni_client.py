import requests
import pandas as pd
import io
import os
from pathlib import Path

RAIZ_PROYECTO = Path(__file__).resolve().parent.parent


class ONIClient:
    URL = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"

    def __init__(self, carpeta_raw: str = None, carpeta_processed: str = None):
        self.carpeta_raw = Path(carpeta_raw) if carpeta_raw else RAIZ_PROYECTO / "data" / "raw"
        self.carpeta_processed = Path(carpeta_processed) if carpeta_processed else RAIZ_PROYECTO / "data" / "processed"

    def descargar_raw(self) -> str:
        respuesta = requests.get(self.URL)
        respuesta.raise_for_status()
        return respuesta.text

    def guardar_raw(self, texto: str) -> None:
        self.carpeta_raw.mkdir(parents=True, exist_ok=True)
        ruta = self.carpeta_raw / "oni_raw.txt"
        with open(ruta, "w", encoding="utf-8") as archivo:
            archivo.write(texto)

    def parsear(self, texto: str) -> pd.DataFrame:
        df = pd.read_csv(io.StringIO(texto), sep=r"\s+")
        df.columns = ["temporada", "anio", "temp_promedio", "anomalia"]
        return df

    def clasificar_evento(self, anomalia: float) -> str:
        if anomalia >= 0.5:
            return "El Nino"
        elif anomalia <= -0.5:
            return "La Nina"
        return "Neutral"

    def ejecutar(self) -> pd.DataFrame:
        texto = self.descargar_raw()
        self.guardar_raw(texto)
        df = self.parsear(texto)
        df["evento"] = df["anomalia"].apply(self.clasificar_evento)

        self.carpeta_processed.mkdir(parents=True, exist_ok=True)
        ruta_salida = self.carpeta_processed / "oni_clasificado.csv"
        df.to_csv(ruta_salida, index=False)
        print(f"Guardado en: {ruta_salida}")
        return df