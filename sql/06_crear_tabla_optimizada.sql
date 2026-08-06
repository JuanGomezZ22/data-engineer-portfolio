CREATE OR REPLACE TABLE `clima_dataset.clima_el_nino_optimizada`
PARTITION BY DATE_TRUNC(fecha, MONTH)
CLUSTER BY ciudad, evento
AS
SELECT
    fecha,
    ciudad,
    precipitacion_mm,
    temp_max,
    temp_min,
    latitud,
    longitud,
    evento,
    anomalia
FROM `clima_dataset.clima_el_nino_completo`;