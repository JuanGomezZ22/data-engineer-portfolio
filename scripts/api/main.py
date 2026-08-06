from fastapi import FastAPI
from google.cloud import bigquery

app = FastAPI()
client = bigquery.Client()

@app.get("/")
def raiz():
    return {"status": "ok", "servicio": "API El Nino"}

@app.get("/estado-nino")
def estado_nino():
    query = """
        SELECT ciudad, fecha, evento, anomalia
        FROM `clima_dataset.clima_el_nino_optimizada`
        WHERE fecha = (SELECT MAX(fecha) FROM `clima_dataset.clima_el_nino_optimizada`)
        ORDER BY ciudad
    """
    filas = client.query(query).result()
    return [dict(fila) for fila in filas]