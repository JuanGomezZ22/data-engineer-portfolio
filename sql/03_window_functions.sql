-- ============================================
-- Window Functions sobre el dataset El Nino Costero
-- ============================================

-- 1. Media movil de 7 dias de precipitacion por ciudad
--    (suaviza el ruido diario, tecnica estandar en analisis climatico)
SELECT
    fecha,
    ciudad,
    precipitacion_mm,
    ROUND(AVG(precipitacion_mm) OVER (
        PARTITION BY ciudad
        ORDER BY fecha
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 2) AS media_movil_7d
FROM read_parquet('data/processed/spark_output/**/*.parquet', hive_partitioning = true)
ORDER BY ciudad, fecha
LIMIT 20;

-- 2. Ranking de los 5 dias mas lluviosos POR ANIO Y CIUDAD (no global)
--    RANK deja huecos si hay empates, DENSE_RANK no
WITH ranking AS (
    SELECT
        fecha,
        ciudad,
        precipitacion_mm,
        EXTRACT(YEAR FROM fecha) AS anio,
        RANK() OVER (
            PARTITION BY ciudad, EXTRACT(YEAR FROM fecha)
            ORDER BY precipitacion_mm DESC
        ) AS ranking_lluvia
    FROM read_parquet('data/processed/spark_output/**/*.parquet', hive_partitioning = true)
)
SELECT * FROM ranking
WHERE ranking_lluvia <= 5
ORDER BY ciudad, anio, ranking_lluvia;

-- 3. LAG: detectar el dia exacto en que un evento climatico CAMBIA
--    (ej. de "Neutral" a "El Nino") -- util como feature de "dias desde el inicio del evento"
WITH eventos_con_anterior AS (
    SELECT
        fecha,
        ciudad,
        evento,
        LAG(evento) OVER (PARTITION BY ciudad ORDER BY fecha) AS evento_dia_anterior
    FROM read_parquet('data/processed/spark_output/**/*.parquet', hive_partitioning = true)
    WHERE evento IS NOT NULL
)
SELECT fecha, ciudad, evento_dia_anterior, evento AS evento_nuevo
FROM eventos_con_anterior
WHERE evento != evento_dia_anterior
ORDER BY ciudad, fecha;

-- 4. Suma acumulada (running total) de precipitacion por ciudad y anio
--    -- responde: "cuanta lluvia acumulada llevamos en lo que va del anio"
SELECT
    fecha,
    ciudad,
    precipitacion_mm,
    ROUND(SUM(precipitacion_mm) OVER (
        PARTITION BY ciudad, EXTRACT(YEAR FROM fecha)
        ORDER BY fecha
    ), 2) AS precipitacion_acumulada_anual
FROM read_parquet('data/processed/spark_output/**/*.parquet', hive_partitioning = true)
WHERE ciudad = 'piura' AND EXTRACT(YEAR FROM fecha) = 2017
ORDER BY fecha
LIMIT 15;