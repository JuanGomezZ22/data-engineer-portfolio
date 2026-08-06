CREATE OR REPLACE MODEL `clima_dataset.modelo_precipitacion`
OPTIONS(
    model_type = 'linear_reg',
    input_label_cols = ['precipitacion_mm'],
    data_split_method = 'AUTO_SPLIT'
) AS
SELECT
    ciudad,
    EXTRACT(MONTH FROM fecha) AS mes,
    evento,
    anomalia,
    temp_max,
    temp_min,
    precipitacion_mm
FROM `clima_dataset.clima_el_nino_optimizada`
WHERE evento IS NOT NULL;