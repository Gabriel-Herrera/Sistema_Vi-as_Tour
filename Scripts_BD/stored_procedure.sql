-- =====================================================================
-- PROCEDIMIENTO ALMACENADO - Proyecto: Gestión de Tours
-- Extracción de datos de visitas a viñas por año
-- =====================================================================
USE `tourviña`;

DROP PROCEDURE IF EXISTS getData;

DELIMITER //

CREATE PROCEDURE getData(IN var INT)
BEGIN
    SELECT 
        v.nombre AS nombre_vina,
        CAST(SUM(r.cant_personas) AS SIGNED) AS total_clientes
    FROM RESERVA r
    JOIN TOUR t ON r.id_tour = t.id_tour
    JOIN VINA v ON t.id_vina = v.id_vina
    WHERE YEAR(t.fec_hora_inicio) = var
      AND r.asistio_tour = 1
      AND r.estado_reserva != 'Cancelada'
    GROUP BY v.nombre;
END //

DELIMITER ;
