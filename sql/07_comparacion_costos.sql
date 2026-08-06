-- Query A: tabla SIN particion optima (solo clustering heredado por ciudad)
SELECT AVG(precipitacion_mm)
FROM `clima_dataset.clima_el_nino_completo`
WHERE fecha BETWEEN '2023-01-01' AND '2023-03-31';

-- Query B: misma pregunta, tabla CON particion por fecha
SELECT AVG(precipitacion_mm)
FROM `clima_dataset.clima_el_nino_optimizada`
WHERE fecha BETWEEN '2023-01-01' AND '2023-03-31';