-- 1. Metricas de calidad del modelo (r2_score, mean_absolute_error, etc.)
SELECT *
FROM ML.EVALUATE(MODEL `clima_dataset.modelo_precipitacion`);

-- 2. Que tanto pesa cada feature en la prediccion (interpretabilidad)
SELECT *
FROM ML.WEIGHTS(MODEL `clima_dataset.modelo_precipitacion`)
ORDER BY ABS(weight) DESC;

-- 3. Curva de entrenamiento (util para ver si convergio bien)
SELECT *
FROM ML.TRAINING_INFO(MODEL `clima_dataset.modelo_precipitacion`);

-- 4. Prediccion sobre un escenario hipotetico:
--    Piura, febrero, en pleno El Nino, con anomalia alta
SELECT
    predicted_precipitacion_mm
FROM ML.PREDICT(MODEL `clima_dataset.modelo_precipitacion`,
    (SELECT
        'piura' AS ciudad,
        2 AS mes,
        'El Nino' AS evento,
        2.0 AS anomalia,
        30.0 AS temp_max,
        22.0 AS temp_min
    )
);