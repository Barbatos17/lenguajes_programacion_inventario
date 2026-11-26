from datetime import datetime
from functools import reduce

import ui
from servicios import leer_entero, leer_texto, mostrar_tabla_productos

# Código de venta automático (closure)


def crear_generador_codigos(inicio=0):
    ultimo = inicio

    def siguiente():
        nonlocal ultimo
        ultimo += 1
        return ultimo

    return siguiente


generar_codigo = crear_generador_codigos()


# Clase Venta


class Venta:
    """Guarda una venta ya confirmada."""

    def __init__(self, codigo, fecha, lineas, total):
        self.codigo = codigo
        self.fecha = fecha
        self.lineas = lineas
        self.total = total

    def descripcion(self):
        return (
            f"Venta #{self.codigo} | {self.fecha} | "
            f"{len(self.lineas)} producto(s) | Total: S/ {self.total:.2f}"
        )


# Lista donde se guardan las ventas confirmadas (en memoria, sin base de datos)
ventas_registradas = []


# Funciones de apoyo


def buscar_por_codigo(inventario, codigo):
    """Devuelve el producto con ese código, o None si no existe."""
    return inventario.obtener(codigo)


def mostrar_productos_disponibles(inventario):
    """Muestra solo los productos con stock mayor a 0."""
    disponibles = list(filter(lambda p: p.stock > 0, inventario.listar()))
    ui.seccion("Productos disponibles")
    if not disponibles:
        ui.mensaje_aviso("No hay productos con stock.")
    else:
        mostrar_tabla_productos(disponibles)
    return disponibles


def calcular_total(inventario, caja):
    """Suma precio x cantidad de cada producto de la caja (map + reduce)."""
    subtotales = map(lambda item: _subtotal_item(inventario, item), caja.items())  # NOSONAR
    return reduce(lambda a, b: a + b, subtotales, 0)

def _subtotal_item(inventario, item):
    codigo, cantidad = item
    return buscar_por_codigo(inventario, codigo).precio * cantidad

def mostrar_resumen(inventario, caja):
    ui.seccion("Resumen de la venta")
    if not caja:
        ui.mensaje_aviso("La caja está vacía.")
        return

    filas = []
    for codigo, cantidad in caja.items():
        p = buscar_por_codigo(inventario, codigo)
        filas.append([
            f"{ui.ACENTO}{codigo}{ui.RESET}",
            p.nombre,
            cantidad,
            f"S/ {p.precio:.2f}",
            f"S/ {p.precio * cantidad:.2f}",
        ])

    total = calcular_total(inventario, caja)
    filas.append([
        "",
        f"{ui.BOLD}TOTAL{ui.RESET}",
        "",
        "",
        f"{ui.BOLD}{ui.OK}S/ {total:.2f}{ui.RESET}",
    ])
    ui.tabla(
        ["CÓDIGO", "PRODUCTO", "CANT.", "P. UNIT.", "SUBTOTAL"],
        filas,
        ["<", "<", ">", ">", ">"],
        pie=1,
    )


def mostrar_ticket(venta):
    ancho = 60
    util = ancho - 4
    lineas = [
        ui.centrar(f"{ui.BOLD}{ui.degradado(ui.NOMBRE_TIENDA)}", util),
        ui.centrar(f"{ui.GRIS}Comprobante de venta{ui.RESET}", util),
        None,
        ui.par(f"{ui.GRIS}Venta N.{ui.RESET}", f"#{venta.codigo:03d}", util),
        ui.par(f"{ui.GRIS}Fecha{ui.RESET}", venta.fecha, util),
        None,
    ]
    for linea in venta.lineas:
        izq = f"{linea['nombre']} x{linea['cantidad']}"
        der = f"S/ {linea['precio'] * linea['cantidad']:.2f}"
        lineas.append(ui.par(izq, der, util))
    lineas += [
        None,
        ui.par(
            f"{ui.BOLD}TOTAL{ui.RESET}",
            f"{ui.BOLD}{ui.OK}S/ {venta.total:.2f}{ui.RESET}",
            util,
        ),
        None,
        ui.centrar(f"{ui.GRIS}Gracias por su compra{ui.RESET}", util),
    ]
    print()
    ui.caja(lineas, "Ticket", ancho)


# La caja (diccionario {codigo: cantidad})


def pedir_producto(inventario, caja):
    """Pide código y cantidad, valida y agrega a la caja."""
    codigo = leer_texto("\nCódigo del producto: ").upper()
    producto = buscar_por_codigo(inventario, codigo)

    if producto is None:
        ui.mensaje_error("Código no encontrado.")
        return

    if producto.stock == 0:
        ui.mensaje_aviso("Ese producto no tiene stock.")
        return

    ya_en_caja = caja.get(codigo, 0)
    disponible = producto.stock - ya_en_caja
    ui.mensaje_info(f"Disponible para agregar: {disponible}")

    cantidad = leer_entero("Cantidad: ")
    if cantidad == 0:
        ui.mensaje_error("La cantidad debe ser mayor a 0.")
        return

    if ya_en_caja + cantidad > producto.stock:
        ui.mensaje_aviso(
            f"Stock no disponible. "
            f"Solo puedes agregar {disponible} unidad(es) de '{producto.nombre}'."
        )
        return

    caja[codigo] = ya_en_caja + cantidad
    ui.mensaje_ok(f"Agregado: {producto.nombre} x {cantidad}")


def quitar_producto(caja):
    """Quita un producto de la caja."""
    if not caja:
        ui.mensaje_aviso("La caja está vacía.")
        return
    codigo = leer_texto("Código del producto a quitar: ").upper()
    if codigo in caja:
        del caja[codigo]
        ui.mensaje_ok(f"Producto {codigo} quitado de la caja.")
    else:
        ui.mensaje_error("Ese producto no está en la caja.")


# Confirmar la venta


def confirmar_venta(inventario, caja):
    """Descuenta el stock, crea la Venta y la guarda."""
    lineas = []
    for codigo, cantidad in caja.items():
        p = buscar_por_codigo(inventario, codigo)
        p.stock -= cantidad
        lineas.append(
            {
                "codigo": codigo,
                "nombre": p.nombre,
                "cantidad": cantidad,
                "precio": p.precio,
            }
        )

    total = sum(linea["precio"] * linea["cantidad"] for linea in lineas)
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    venta = Venta(generar_codigo(), fecha, lineas, total)
    ventas_registradas.append(venta)
    return venta


# Opción 4 del menú


def registrar_venta(inventario):
    ui.seccion("Registrar venta")
    caja = {}

    mostrar_productos_disponibles(inventario)

    while True:
        ui.seccion("¿Qué deseas hacer?")
        if caja:
            ui.mensaje_info(
                f"En caja: {len(caja)} producto(s) | "
                f"Total parcial: S/ {calcular_total(inventario, caja):.2f}"
            )
        ui.opciones([
            ("1", "Agregar producto"),
            ("2", "Quitar producto"),
            ("3", "Terminar y ver resumen"),
            ("0", "Cancelar venta"),
        ])
        opcion = ui.pedir("Elige una opción: ")

        if opcion == "1":
            pedir_producto(inventario, caja)
        elif opcion == "2":
            quitar_producto(caja)
        elif opcion == "3":
            if not caja:
                ui.mensaje_error("No hay productos en la caja.")
                continue
            mostrar_resumen(inventario, caja)
            respuesta = leer_texto("\n¿Confirmar venta? (s/n): ").lower()
            if respuesta == "s":
                ui.cargando("Procesando venta", 0.8)
                venta = confirmar_venta(inventario, caja)
                mostrar_ticket(venta)
                print()
                ui.mensaje_ok(
                    f"Venta #{venta.codigo} registrada. "
                    f"Total: S/ {venta.total:.2f}"
                )
                return
            ui.mensaje_aviso("Aún puedes seguir editando la caja.")
        elif opcion == "0":
            print()
            ui.mensaje_aviso("Venta cancelada. El stock no cambió.")
            return
        else:
            ui.mensaje_error("Opción inválida.")

# ---------- Opción 8: Reportes de ventas (reduce + agregación por parámetro) ----------


def agregar_ventas(lista_ventas, fn_agregacion, valor_inicial=0):
    """Función de orden superior: aplica una función de agregación usando reduce."""
    return reduce(fn_agregacion, lista_ventas, valor_inicial)


def agg_ingresos_totales(acumulado, venta):
    return acumulado + venta.total


def agg_unidades_vendidas(acumulado, venta):
    return acumulado + sum(linea["cantidad"] for linea in venta.lineas)


def agg_venta_mayor(actual, venta):
    if actual is None or venta.total > actual.total:
        return venta
    return actual


def agg_venta_menor(actual, venta):
    if actual is None or venta.total < actual.total:
        return venta
    return actual


def exportar_reporte_csv(ventas, total_ingresos, total_unidades, promedio):
    """Genera un archivo CSV con el detalle de ventas y el resumen."""
    marca_tiempo = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"reporte_ventas_{marca_tiempo}.csv"

    # utf-8-sig asegura que Excel muestre bien tildes y símbolos
    with open(nombre_archivo, mode="w", newline="", encoding="utf-8-sig") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow([
            "venta_id", "fecha", "codigo_producto", "producto",
            "cantidad", "precio_unitario", "subtotal", "total_venta"
        ])

        for v in ventas:
            for linea in v.lineas:
                escritor.writerow([
                    f"#{v.codigo:03d}",
                    v.fecha,
                    linea["codigo"],
                    linea["nombre"],
                    linea["cantidad"],
                    f"{linea['precio']:.2f}",
                    f"{linea['precio'] * linea['cantidad']:.2f}",
                    f"{v.total:.2f}",
                ])

        escritor.writerow([])
        escritor.writerow(["RESUMEN", "VALOR"])
        escritor.writerow(["Total de ventas", len(ventas)])
        escritor.writerow(["Unidades vendidas", total_unidades])
        escritor.writerow(["Ticket promedio (S/)", f"{promedio:.2f}"])
        escritor.writerow(["Ingresos totales (S/)", f"{total_ingresos:.2f}"])

    return nombre_archivo


def reporte_ventas():
    ui.seccion("Reportes de ventas")

    if not ventas_registradas:
        ui.mensaje_aviso("No hay ventas registradas todavía.")
        return

    # Agregaciones usando reduce + función pasada como parámetro
    total_ingresos = agregar_ventas(ventas_registradas, agg_ingresos_totales, 0.0)
    total_unidades = agregar_ventas(ventas_registradas, agg_unidades_vendidas, 0)
    mayor = agregar_ventas(ventas_registradas, agg_venta_mayor, None)
    menor = agregar_ventas(ventas_registradas, agg_venta_menor, None)
    promedio = total_ingresos / len(ventas_registradas)

    print()
    ui.tarjetas([
        ("VENTAS", len(ventas_registradas), ui.PRIMARIO),
        ("UNIDADES", total_unidades, ui.ACENTO),
        ("TICKET PROM.", f"S/ {promedio:.2f}", ui.PRIMARIO),
        ("INGRESOS", f"S/ {total_ingresos:.2f}", ui.OK),
    ])

    # 1) Tabla resumen por venta
    filas_resumen = []
    for v in ventas_registradas:
        unidades_v = sum(linea["cantidad"] for linea in v.lineas)
        resumen_prods = ", ".join(f"{l['nombre']} x{l['cantidad']}" for l in v.lineas)
        filas_resumen.append([
            f"{ui.ACENTO}#{v.codigo:03d}{ui.RESET}",
            v.fecha,
            resumen_prods[:38] + ("..." if len(resumen_prods) > 38 else ""),
            unidades_v,
            f"S/ {v.total:.2f}",
            ])

    filas_resumen.append([
        "",
        f"{ui.BOLD}TOTAL{ui.RESET}",
        f"{len(ventas_registradas)} venta(s)",
        f"{ui.BOLD}{total_unidades}{ui.RESET}",
        f"{ui.BOLD}{ui.OK}S/ {total_ingresos:.2f}{ui.RESET}",
    ])

    ui.seccion("Resumen por venta")
    ui.tabla(
        ["VENTA", "FECHA", "PRODUCTOS", "UNID.", "TOTAL"],
        filas_resumen,
        ["<", "<", "<", ">", ">"],
        pie=1,
    )

    # 2) Tabla detallada (espejo de las filas del CSV)
    filas_detalle = []
    for v in ventas_registradas:
        for l in v.lineas:
            filas_detalle.append([
                f"{ui.ACENTO}#{v.codigo:03d}{ui.RESET}",
                l["codigo"],
                l["nombre"][:30] + ("..." if len(l["nombre"]) > 30 else ""),
                l["cantidad"],
                f"S/ {l['precio']:.2f}",
                f"S/ {l['precio'] * l['cantidad']:.2f}",
                ])

    ui.seccion("Detalle exportado (línea por línea)")
    ui.tabla(
        ["VENTA", "CÓDIGO", "PRODUCTO", "CANT.", "P. UNIT.", "SUBTOTAL"],
        filas_detalle,
        ["<", "<", "<", ">", ">", ">"],
    )

    print()
    ui.mensaje_info(
        f"Venta más alta: #{mayor.codigo:03d} (S/ {mayor.total:.2f}) | "
        f"Venta más baja: #{menor.codigo:03d} (S/ {menor.total:.2f})"
    )

    nombre_csv = exportar_reporte_csv(
        ventas_registradas, total_ingresos, total_unidades, promedio
    )
    print()
    ui.mensaje_ok(f"Reporte mostrado en consola y exportado a '{nombre_csv}'.")