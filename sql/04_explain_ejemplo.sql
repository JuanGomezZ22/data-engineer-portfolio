EXPLAIN
SELECT
    ciudad,
    ROUND(AVG(precipitacion_mm), 2) AS precipitacion_promedio
FROM read_parquet('data/processed/spark_output/**/*.parquet', hive_partitioning = true)
WHERE ciudad = 'piura'
GROUP BY ciudad;