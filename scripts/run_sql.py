import duckdb
import sys
from pathlib import Path

RAIZ_PROYECTO = Path(__file__).resolve().parent.parent


def limpiar_bloque(bloque: str) -> str:
    lineas_utiles = [
        linea for linea in bloque.splitlines()
        if linea.strip() and not linea.strip().startswith("--")
    ]
    return "\n".join(lineas_utiles).strip()


def ejecutar_queries(ruta_archivo: Path):
    contenido = ruta_archivo.read_text(encoding="utf-8")
    bloques = contenido.split(";")

    con = duckdb.connect()
    contador = 0

    for bloque in bloques:
        query_limpia = limpiar_bloque(bloque)
        if not query_limpia:
            continue

        contador += 1
        print(f"\n{'='*60}\nQuery {contador}\n{'='*60}")
        resultado = con.execute(query_limpia).fetchdf()
        print(resultado.to_string(index=False))

    if contador == 0:
        print("No se encontro ninguna query ejecutable en el archivo.")


if __name__ == "__main__":
    nombre_archivo = sys.argv[1] if len(sys.argv) > 1 else "01_exploracion_basica.sql"
    ruta_sql = RAIZ_PROYECTO / "sql" / nombre_archivo
    ejecutar_queries(ruta_sql)