from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pathlib import Path

RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
RUTA_CLIMA = RAIZ_PROYECTO / "data" / "processed" / "clima_el_nino_maestro.csv"
RUTA_ONI = RAIZ_PROYECTO / "data" / "processed" / "oni_clasificado.csv"
RUTA_SALIDA = RAIZ_PROYECTO / "data" / "processed" / "spark_output"

# Cada mes es el "mes central" de una temporada ONI (ver explicacion Paso 3 anterior)
MAPEO_TEMPORADA = {
    1: "DJF", 2: "JFM", 3: "FMA", 4: "MAM", 5: "AMJ", 6: "MJJ",
    7: "JJA", 8: "JAS", 9: "ASO", 10: "SON", 11: "OND", 12: "NDJ",
}


def crear_sesion_spark() -> SparkSession:
    return (
        SparkSession.builder
        .appName("ElNinoJoin")
        .master("local[*]")
        # Spark reparte por defecto en 200 particiones al hacer shuffle (join/groupBy).
        # Para un dataset chico eso es un desperdicio de overhead -> lo bajamos a 8.
        # En un cluster real (Dataproc/GKE), ajustar esto mal significa pagar por
        # cientos de tareas vacias o, al reves, saturar pocos nodos.
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )


def cargar_datos(spark: SparkSession):
    df_clima = spark.read.csv(str(RUTA_CLIMA), header=True, inferSchema=True)
    df_oni = spark.read.csv(str(RUTA_ONI), header=True, inferSchema=True)
    return df_clima, df_oni


def agregar_columnas_temporada(df_clima):
    # OPTIMIZACION CLAVE: usamos funciones nativas de Spark (F.month, F.year,
    # create_map), NO un UDF de Python. Un UDF de Python obliga a Spark a
    # serializar cada fila entre la JVM y el interprete Python -> mucho mas
    # lento, y en un cluster real eso se traduce directamente en mas tiempo
    # de computo facturado.
    df = df_clima.withColumn("mes", F.month("fecha"))
    df = df.withColumn("anio_temporada", F.year("fecha"))

    mapeo_expr = F.create_map([F.lit(x) for par in MAPEO_TEMPORADA.items() for x in par])
    df = df.withColumn("temporada", mapeo_expr[F.col("mes")])
    return df


def ejecutar_join(df_clima_con_temporada, df_oni):
    # OPTIMIZACION: seleccionamos solo las columnas necesarias ANTES del join
    # (column pruning) -> reduce el volumen de datos que Spark mueve en el shuffle.
    df_oni_reducido = df_oni.select(
        F.col("temporada").alias("temporada_oni"),
        F.col("anio").alias("anio_oni"),
        "evento",
        "anomalia",
    )

    return df_clima_con_temporada.join(
        df_oni_reducido,
        (df_clima_con_temporada.temporada == df_oni_reducido.temporada_oni) &
        (df_clima_con_temporada.anio_temporada == df_oni_reducido.anio_oni),
        how="left",
    ).drop("temporada_oni", "anio_oni")


if __name__ == "__main__":
    spark = crear_sesion_spark()

    df_clima, df_oni = cargar_datos(spark)
    df_clima_temporada = agregar_columnas_temporada(df_clima)
    df_final = ejecutar_join(df_clima_temporada, df_oni)

    print("--- Muestra del resultado ---")
    df_final.select("fecha", "ciudad", "precipitacion_mm", "temp_max", "evento", "anomalia").show(10)

    print("--- Conteo de dias por tipo de evento ---")
    df_final.groupBy("evento").count().show()

    # Guardamos en Parquet particionado por ciudad: formato columnar y comprimido.
    # Cuando en el futuro filtremos por ciudad en BigQuery/GCS, solo se leera esa
    # particion, no el dataset completo -> ahorro real de costo (Paso 7-8).
    df_final.write.mode("overwrite").partitionBy("ciudad").parquet(str(RUTA_SALIDA))
    print(f"\nGuardado en: {RUTA_SALIDA}")

    spark.stop()