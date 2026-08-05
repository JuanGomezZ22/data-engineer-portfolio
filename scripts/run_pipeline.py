import os
from datetime import date
from weather_extractor import WeatherExtractor
from weather_transformer import WeatherTransformer
from oni_client import ONIClient

CIUDADES = {
    "piura": {"lat": -5.19, "lon": -80.63},
    "tumbes": {"lat": -3.57, "lon": -80.45},
    "chiclayo": {"lat": -6.77, "lon": -79.84},
    "trujillo": {"lat": -8.11, "lon": -79.02},
    "lima": {"lat": -12.05, "lon": -77.04},
}

FECHA_INICIO = os.environ.get("FECHA_INICIO", "2010-01-01")
FECHA_FIN = os.environ.get("FECHA_FIN", date.today().isoformat())

if __name__ == "__main__":
    extractor = WeatherExtractor(CIUDADES, FECHA_INICIO, FECHA_FIN)
    extractor.ejecutar()

    transformer = WeatherTransformer()
    df_clima = transformer.ejecutar(list(CIUDADES.keys()))

    oni_client = ONIClient()
    df_oni = oni_client.ejecutar()

    print("\nPipeline completo ejecutado con éxito.")