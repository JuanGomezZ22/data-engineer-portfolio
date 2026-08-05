-- ============================================
-- Exploracion basica del dataset El Nino Costero
-- Fuente: data/processed/spark_output/ (Parquet particionado por ciudad)
-- ============================================

-- 1. Total de registros y rango de fechas disponible
SELECT
    COUNT(*) AS total_filas,
    MIN(fecha) AS fecha_minima,
    MAX(fecha) AS fecha_maxima
FROM read_parquet('data/processed/spark_output/**/*.parquet', hive_partitioning = true);

-- 2. Precipitacion promedio y maxima por ciudad
SELECT
    ciudad,
    ROUND(AVG(precipitacion_mm), 2) AS precipitacion_promedio,
    ROUND(MAX(precipitacion_mm), 2) AS precipitacion_maxima,
    COUNT(*) AS dias_registrados
FROM read_parquet('data/processed/spark_output/**/*.parquet', hive_partitioning = true)
GROUP BY ciudad
ORDER BY precipitacion_promedio DESC;

-- 3. Los 10 dias mas lluviosos de todo el dataset
SELECT
    fecha,
    ciudad,
    precipitacion_mm,
    evento
FROM read_parquet('data/processed/spark_output/**/*.parquet', hive_partitioning = true)
WHERE precipitacion_mm IS NOT NULL
ORDER BY precipitacion_mm DESC
LIMIT 10;

-- 4. Distribucion de dias por tipo de evento (El Nino / La Nina / Neutral), por ciudad
SELECT
    ciudad,
    evento,
    COUNT(*) AS dias,
    ROUND(AVG(precipitacion_mm), 2) AS precipitacion_promedio
FROM read_parquet('data/processed/spark_output/**/*.parquet', hive_partitioning = true)
WHERE evento IS NOT NULL
GROUP BY ciudad, evento
ORDER BY ciudad, evento;

-- 5. Filtro por rango de fechas: el Nino Costero de 2017
SELECT
    ciudad,
    ROUND(AVG(precipitacion_mm), 2) AS precipitacion_promedio_2017
FROM read_parquet('data/processed/spark_output/**/*.parquet', hive_partitioning = true)
WHERE fecha BETWEEN '2017-01-01' AND '2017-04-30'
GROUP BY ciudad
ORDER BY precipitacion_promedio_2017 DESC;