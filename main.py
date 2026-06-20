import pymysql
import sys
import matplotlib.pyplot as plt

def get_connection():
    try:
        # Connects to MySQL using latin1 or utf8 to avoid issues with tourviña name
        return pymysql.connect(
            host='localhost',
            user='root',
            password='',
            db='tourvi\xf1a', # 'tourviña' in latin-1
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    except Exception as e:
        print(f"\n[ERROR] No se pudo conectar a la base de datos: {e}")
        print("Asegúrate de que XAMPP y MySQL estén activos y la base de datos 'tourviña' esté creada.\n")
        sys.exit(1)

def mostrar_menu():
    print("\n" + "="*80)
    print("      SISTEMA DE GESTIÓN DE TOURS Y VENTAS - VIÑAS DE CHILE (FASE 2)      ")
    print("="*80)
    print("1. Tour realizado con clientes y valoraciones por fecha específica")
    print("2. Resumen anual de reservas de los distintos tours")
    print("3. Consolidado de ventas de productos por viña")
    print("4. Informe de ganancias del último año superiores al promedio")
    print("5. Informe de ganancias consolidado entre dos años específicos")
    print("6. Generar Gráfico de Sectores: Visitas por Viña en un año (Stored Proc)")
    print("7. Salir")
    print("="*80)

def requerimiento_1():
    print("\n--- 1. Clientes y Valoraciones por Fecha ---")
    fecha = input("Ingresa la fecha (YYYY-MM-DD) [Por defecto: 2026-07-01]: ").strip()
    if not fecha:
        fecha = "2026-07-01"
        
    sql = """
        SELECT 
            t.id_tour,
            t.nombre_tour,
            v.nombre AS nombre_vina,
            t.fec_hora_inicio,
            c.id_cliente,
            CONCAT(c.nombres, ' ', c.apellidos) AS cliente,
            r.cant_personas,
            COALESCE(val.puntuacion, 'Sin Nota') AS puntuacion,
            COALESCE(val.comentario, 'Sin Comentario') AS comentario
        FROM TOUR t
        JOIN VINA v ON t.id_vina = v.id_vina
        JOIN RESERVA r ON t.id_tour = r.id_tour
        JOIN CLIENTE c ON r.id_cliente = c.id_cliente
        LEFT JOIN VALORACION val ON (val.id_tour = t.id_tour AND val.id_cliente = c.id_cliente)
        WHERE DATE(t.fec_hora_inicio) = %s
          AND r.asistio_tour = 1
    """
    
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (fecha,))
            results = cursor.fetchall()
            if not results:
                print(f"No se encontraron visitas registradas o asistidas para la fecha: {fecha}")
                return
            
            print(f"\nResultados para la fecha {fecha}:")
            print(f"{'Tour':<25} | {'Viña':<25} | {'Cliente':<25} | {'Cant':<4} | {'Nota':<8} | {'Comentario'}")
            print("-" * 120)
            for row in results:
                tour = row['nombre_tour'][:24]
                vina = row['nombre_vina'][:24]
                cliente = row['cliente'][:24]
                cant = row['cant_personas']
                nota = str(row['puntuacion'])
                com = row['comentario'][:30]
                print(f"{tour:<25} | {vina:<25} | {cliente:<25} | {cant:<4} | {nota:<8} | {com}")
    except Exception as e:
        print(f"Error al ejecutar la consulta: {e}")
    finally:
        conn.close()

def requerimiento_2():
    print("\n--- 2. Resumen Anual de Reservas por Tour ---")
    sql = """
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
        ORDER BY anio DESC, total_reservas DESC
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            results = cursor.fetchall()
            if not results:
                print("No hay reservas registradas en el sistema.")
                return
            
            print(f"{'Año':<4} | {'Tour':<25} | {'Viña':<25} | {'Reservas':<8} | {'Pasajeros':<9} | {'Recaudado'}")
            print("-" * 100)
            for row in results:
                print(f"{row['anio']:<4} | {row['nombre_tour'][:24]:<25} | {row['nombre_vina'][:24]:<25} | {row['total_reservas']:<8} | {row['total_personas_inscritas']:<9} | ${row['total_recaudado']:,.0f}")
    except Exception as e:
        print(f"Error al ejecutar la consulta: {e}")
    finally:
        conn.close()

def requerimiento_3():
    print("\n--- 3. Consolidado de Ventas de Productos por Viña ---")
    sql = """
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
        ORDER BY v.nombre, total_ventas_brutas DESC
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            results = cursor.fetchall()
            if not results:
                print("No hay ventas de productos registradas.")
                return
            
            print(f"{'Viña':<25} | {'Producto':<30} | {'Tipo':<15} | {'Vendidos':<8} | {'Monto Bruto':<12} | {'Descuentos'}")
            print("-" * 110)
            for row in results:
                print(f"{row['nombre_vina'][:24]:<25} | {row['nombre_producto'][:29]:<30} | {row['tipo_vino'][:14]:<15} | {row['cantidad_vendida']:<8} | ${row['total_ventas_brutas']:<11,.0f} | ${row['total_descuentos_aplicados']:,.0f}")
    except Exception as e:
        print(f"Error al ejecutar la consulta: {e}")
    finally:
        conn.close()

def requerimiento_4():
    print("\n--- 4. Ganancias del Último Año Superiores al Promedio Mensual ---")
    sql = """
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
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            results = cursor.fetchall()
            if not results:
                print("No se encontraron ganancias para el último año que superen el promedio.")
                return
            
            # Print average
            avg_val = results[0]['promedio_mensual']
            print(f"Promedio mensual de ganancias del último año: ${avg_val:,.2f}\n")
            
            print(f"{'Mes/Periodo':<12} | {'Ingresos Tours':<15} | {'Ingresos Productos':<18} | {'Ganancias Totales'}")
            print("-" * 70)
            for row in results:
                print(f"{row['periodo']:<12} | ${row['ingresos_tours']:<14,.0f} | ${row['ingresos_productos']:<17,.0f} | ${row['ganancias_totales']:,.0f}")
    except Exception as e:
        print(f"Error al ejecutar la consulta: {e}")
    finally:
        conn.close()

def requerimiento_5():
    print("\n--- 5. Ganancias Consolidadas entre 2 Años ---")
    try:
        anio_inicio = int(input("Ingresa el año de inicio (ej. 2025): ").strip())
        anio_fin = int(input("Ingresa el año de fin (ej. 2026): ").strip())
    except ValueError:
        print("Entrada inválida. Debes ingresar números enteros para los años.")
        return

    sql = """
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
        WHERE YEAR(periodos.fecha) BETWEEN %s AND %s
        GROUP BY YEAR(periodos.fecha)
        ORDER BY anio DESC
    """
    
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (anio_inicio, anio_fin))
            results = cursor.fetchall()
            if not results:
                print(f"No hay registros de ganancias entre los años {anio_inicio} y {anio_fin}.")
                return
            
            print(f"\nGanancias entre {anio_inicio} y {anio_fin}:")
            print(f"{'Año':<6} | {'Ingresos Tours':<16} | {'Ingresos Productos':<18} | {'Ganancias Totales'}")
            print("-" * 70)
            for row in results:
                print(f"{row['anio']:<6} | ${row['ingresos_tours']:<15,.0f} | ${row['ingresos_productos']:<17,.0f} | ${row['ganancias_totales']:,.0f}")
    except Exception as e:
        print(f"Error al ejecutar la consulta: {e}")
    finally:
        conn.close()

def requerimiento_6():
    print("\n--- 6. Gráfico de Sectores: Visitas por Viña ---")
    try:
        anio = int(input("Ingresa el año a graficar (ej. 2025 o 2026): ").strip())
    except ValueError:
        print("Entrada inválida. Debes ingresar un año entero.")
        return

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # Call stored procedure getData
            cursor.callproc('getData', (anio,))
            results = cursor.fetchall()
            
            if not results:
                print(f"No hay registros de visitas registradas/asistidas para el año {anio}.")
                return
            
            # Extract data for plotting
            viñas = []
            clientes = []
            for row in results:
                viñas.append(row['nombre_vina'])
                clientes.append(int(row['total_clientes']))
            
            # Print table summary in console
            print(f"\nDatos de visitas para el año {anio}:")
            print(f"{'Viña':<35} | {'Número de Visitantes'}")
            print("-" * 60)
            for v, c in zip(viñas, clientes):
                print(f"{v:<35} | {c}")
            
            # Plotting professional doughnut chart
            print("\nGenerando gráfico de sectores profesional...")
            fig, ax = plt.subplots(figsize=(13, 9))
            
            # Curated modern color palette skipping light blue/teal (approx 0.35 to 0.60 in viridis)
            import numpy as np
            n_viñas = len(viñas)
            n_half1 = n_viñas // 2
            n_half2 = n_viñas - n_half1
            vals = np.concatenate([
                np.linspace(0.0, 0.32, n_half1),
                np.linspace(0.62, 0.95, n_half2)
            ])
            colors = plt.cm.viridis(vals)
            
            # Subtle explosion on all slices for separation
            explode = [0.10] * len(viñas)
            
            # Pie Chart with shadow and selective percentages (hide < 3%)
            wedges, texts, autotexts = ax.pie(
                clientes, 
                explode=explode,
                autopct=lambda p: f'{p:.1f}%' if p >= 3.0 else '',
                startangle=140,
                colors=colors,
                shadow=True,
                pctdistance=0.80, # push percentages outwards
                textprops=dict(color="white", weight="bold", fontsize=9)
            )
            
            # Turn it into a Doughnut chart by adding a center circle
            centre_circle = plt.Circle((0,0), 0.60, fc='white')
            ax.add_artist(centre_circle)
            
            # Add total count text in the center of the doughnut
            total_visitors = sum(clientes)
            ax.text(0, 0, f'Total\n{total_visitors:,}\nvis.', ha='center', va='center', fontsize=14, weight='bold', color='#2c3e50')
            
            # Equal aspect ratio ensures that pie is drawn as a circle
            ax.axis('equal')  
            
            # Title with premium styling
            plt.title(f"Distribución de Visitantes por Viña - Año {anio}", fontsize=16, weight='bold', pad=25, color='#2c3e50')
            
            # Create descriptive legend labels: "Viña Name (Count)"
            legend_labels = [f"{v} ({c} pers.)" for v, c in zip(viñas, clientes)]
            
            # Styled Legend Box on the right
            ax.legend(
                wedges, 
                legend_labels,
                title="Viñas Chilenas",
                loc="center left",
                bbox_to_anchor=(1.05, 0.5),
                fontsize=9,
                frameon=True,
                shadow=True,
                facecolor='#fcfcfc',
                edgecolor='#d1d8e0'
            )
            
            plt.tight_layout()
            
            # Show interactive Matplotlib window
            plt.show()
            print("Gráfico cerrado.")
            
    except Exception as e:
        print(f"Error al ejecutar el procedimiento almacenado o graficar: {e}")
    finally:
        conn.close()

def main():
    while True:
        mostrar_menu()
        opcion = input("Selecciona una opción (1-7): ").strip()
        if opcion == '1':
            requerimiento_1()
        elif opcion == '2':
            requerimiento_2()
        elif opcion == '3':
            requerimiento_3()
        elif opcion == '4':
            requerimiento_4()
        elif opcion == '5':
            requerimiento_5()
        elif opcion == '6':
            requerimiento_6()
        elif opcion == '7':
            print("\n¡Gracias por utilizar el sistema! Saliendo...")
            sys.exit(0)
        else:
            print("\nOpción no válida. Inténtalo de nuevo.")

if __name__ == '__main__':
    main()
