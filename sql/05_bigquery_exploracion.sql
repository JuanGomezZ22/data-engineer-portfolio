SELECT
    ciudad,
    evento,
    ROUND(AVG(precipitacion_mm), 2) AS precipitacion_promedio,
    COUNT(*) AS dias
FROM `clima_dataset.clima_el_nino_completo`
WHERE evento IS NOT NULL
GROUP BY ciudad, evento
ORDER BY ciudad, evento;