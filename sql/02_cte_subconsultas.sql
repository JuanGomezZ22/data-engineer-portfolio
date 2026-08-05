-- ============================================
-- CTEs y Subqueries sobre el dataset El Nino Costero
-- ============================================

-- 1. CTEs encadenados: el ano mas lluvioso por ciudad
--    (2 CTEs: uno agrega por anio, el segundo encuentra el maximo por ciudad)
WITH precipitacion_anual AS (
    SELECT
        ciudad,
        EXTRACT(YEAR FROM fecha) AS anio,
        SUM(precipitacion_mm) AS precipitacion_total
    FROM read_parquet('data/processed/spark_output/**/*.parquet', hive_partitioning = true)
    GROUP BY ciudad, EXTRACT(YEAR FROM fecha)
),
maximo_por_ciudad AS (
    SELECT ciudad, MAX(precipitacion_total) AS max_precipitacion
    FROM precipitacion_anual
    GROUP BY ciudad
)
SELECT
    pa.ciudad,
    pa.anio,
    pa.precipitacion_total
FROM precipitacion_anual pa
JOIN maximo_por_ciudad mc
    ON pa.ciudad = mc.ciudad
    AND pa.precipitacion_total = mc.max_precipitacion
ORDER BY pa.ciudad;

-- 2. CTE con CASE: comparar precipitacion promedio en anios El Nino vs el resto
WITH clasificado AS (
    SELECT
        ciudad,
        precipitacion_mm,
        CASE WHEN evento = 'El Nino' THEN 'Nino' ELSE 'No Nino' END AS grupo
    FROM read_parquet('data/processed/spark_output/**/*.parquet', hive_partitioning = true)
    WHERE evento IS NOT NULL
)
SELECT
    ciudad,
    grupo,
    ROUND(AVG(precipitacion_mm), 2) AS precipitacion_promedio,
    COUNT(*) AS dias
FROM clasificado
GROUP BY ciudad, grupo
ORDER BY ciudad, grupo;

-- 3. Subquery escalar en HAVING: ciudades cuyo promedio en El Nino
--    supera el promedio GLOBAL de precipitacion (todas las ciudades, todo el periodo)
SELECT
    ciudad,
    ROUND(AVG(precipitacion_mm), 2) AS precipitacion_promedio_nino
FROM read_parquet('data/processed/spark_output/**/*.parquet', hive_partitioning = true)
WHERE evento = 'El Nino'
GROUP BY ciudad
HAVING AVG(precipitacion_mm) > (
    SELECT AVG(precipitacion_mm)
    FROM read_parquet('data/processed/spark_output/**/*.parquet', hive_partitioning = true)
)
ORDER BY precipitacion_promedio_nino DESC;

-- 4. Subquery correlacionada: dias con precipitacion por encima
--    del PROPIO promedio de esa ciudad (no del promedio global)
SELECT
    t1.ciudad,
    COUNT(*) AS dias_sobre_su_propio_promedio
FROM read_parquet('data/processed/spark_output/**/*.parquet', hive_partitioning = true) t1
WHERE t1.precipitacion_mm > (
    SELECT AVG(t2.precipitacion_mm)
    FROM read_parquet('data/processed/spark_output/**/*.parquet', hive_partitioning = true) t2
    WHERE t2.ciudad = t1.ciudad
)
GROUP BY t1.ciudad
ORDER BY dias_sobre_su_propio_promedio DESC;