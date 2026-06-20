-- =====================================================================
-- CONSULTAS DE VERIFICACIÓN DE REQUERIMIENTOS DE NEGOCIO (Fase 2)
-- Proyecto: Gestión de Tour y Venta de Productos Viñas de Chile
-- =====================================================================
USE `tourviña`;

-- 1. Tour realizado con los clientes que asistieron en un día específico, 
--    con todo el detalle de sus valoraciones.
--    (Ejemplo para el día '2026-07-01')
SELECT 
    t.id_tour,
    t.nombre_tour,
    v.nombre AS nombre_vina,
    t.fec_hora_inicio,
    c.id_cliente,
    CONCAT(c.nombres, ' ', c.apellidos) AS cliente,
    r.cant_personas,
    val.puntuacion,
    val.comentario,
    val.fec_valoracion
FROM TOUR t
JOIN VINA v ON t.id_vina = v.id_vina
JOIN RESERVA r ON t.id_tour = r.id_tour
JOIN CLIENTE c ON r.id_cliente = c.id_cliente
LEFT JOIN VALORACION val ON (val.id_tour = t.id_tour AND val.id_cliente = c.id_cliente)
WHERE DATE(t.fec_hora_inicio) = '2026-07-01'
  AND r.asistio_tour = 1;


-- 2. Reserva de los distintos tours en todo el año.
--    Agrupa la cantidad de reservas, pasajeros inscritos y montos totales 
--    recaudados por año y por tour.
SELECT 
    YEAR(r.fec_reserva) AS anio,
    t.nombre_tour,
    v.nombre AS nombre_vina,
    COUNT(r.id_reserva) AS total_reservas,
    SUM(r.cant_personas) AS total_personas_inscritas,
    SUM(r.monto_total) AS total_recaudado
FROM RESERVA r
JOIN TOUR t ON r.id_tour = t.id_tour
JOIN VINA v ON t.id_vina = v.id_vina
GROUP BY YEAR(r.fec_reserva), t.id_tour, t.nombre_tour, v.nombre
ORDER BY anio DESC, total_reservas DESC;


-- 3. Ventas de productos en las distintas viñas.
--    Permite consolidar la cantidad de botellas vendidas y los montos 
--    totales brutos y descuentos por producto en cada viña.
SELECT 
    v.nombre AS nombre_vina,
    p.nombre AS nombre_producto,
    p.tipo_vino,
    SUM(dv.cantidad) AS cantidad_vendida,
    SUM(dv.cantidad * dv.precio_historico) AS total_ventas_brutas,
    SUM(cv.descuento_aplicado) AS total_descuentos_aplicados
FROM DETALLE_VENTA dv
JOIN PRODUCTO p ON dv.id_producto = p.id_producto
JOIN COMPROBANTE_VENTA cv ON dv.id_comprobante = cv.id_comprobante
JOIN VINA v ON cv.id_vina = v.id_vina
GROUP BY v.id_vina, v.nombre, p.id_producto, p.nombre, p.tipo_vino
ORDER BY v.nombre, total_ventas_brutas DESC;


-- 4. Informe de ganancias del último año que incluya las ventas de productos y 
--    de tours mayor al promedio mensual de ese mismo año.
WITH GananciasMensuales AS (
    SELECT 
        DATE_FORMAT(periodos.fecha, '%Y-%m') AS periodo,
        SUM(CASE WHEN concepto = 'Tours' THEN total ELSE 0 END) AS ingresos_tours,
        SUM(CASE WHEN concepto = 'Productos' THEN total ELSE 0 END) AS ingresos_productos,
        SUM(total) AS ganancias_totales
    FROM (
        SELECT fec_reserva AS fecha, 'Tours' AS concepto, monto_total AS total
        FROM RESERVA
        WHERE estado_pago = 'Pagado' AND estado_reserva != 'Cancelada'
          AND YEAR(fec_reserva) = (SELECT MAX(YEAR(fec_reserva)) FROM RESERVA)
        
        UNION ALL
        
        SELECT fec_venta AS fecha, 'Productos' AS concepto, total_final AS total
        FROM COMPROBANTE_VENTA
        WHERE YEAR(fec_venta) = (SELECT MAX(YEAR(fec_reserva)) FROM RESERVA)
    ) AS periodos
    GROUP BY DATE_FORMAT(periodos.fecha, '%Y-%m')
),
PromedioAnual AS (
    SELECT AVG(ganancias_totales) AS promedio_mensual
    FROM GananciasMensuales
)
SELECT 
    gm.periodo,
    gm.ingresos_tours,
    gm.ingresos_productos,
    gm.ganancias_totales,
    ROUND(pa.promedio_mensual, 2) AS promedio_mensual
FROM GananciasMensuales gm
CROSS JOIN PromedioAnual pa
WHERE gm.ganancias_totales > pa.promedio_mensual
ORDER BY gm.periodo DESC;


-- 5. Informe de ganancias entre 2 años ingresados por el usuario que incluya las 
--    ventas de productos y de tours.
--    (Ejemplo para los años 2025 y 2026, parametrizado en la aplicación de Python)
SELECT 
    YEAR(periodos.fecha) AS anio,
    SUM(CASE WHEN concepto = 'Tours' THEN total ELSE 0 END) AS ingresos_tours,
    SUM(CASE WHEN concepto = 'Productos' THEN total ELSE 0 END) AS ingresos_productos,
    SUM(total) AS ganancias_totales
FROM (
    SELECT fec_reserva AS fecha, 'Tours' AS concepto, monto_total AS total
    FROM RESERVA
    WHERE estado_pago = 'Pagado' AND estado_reserva != 'Cancelada'
    
    UNION ALL
    
    SELECT fec_venta AS fecha, 'Productos' AS concepto, total_final AS total
    FROM COMPROBANTE_VENTA
) AS periodos
WHERE YEAR(periodos.fecha) BETWEEN 2025 AND 2026  -- Valores parametrizados
GROUP BY YEAR(periodos.fecha)
ORDER BY anio DESC;
