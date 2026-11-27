from datetime import datetime
from functools import reduce

import ui
from servicios import leer_entero, leer_texto, mostrar_tabla_productos

# Código de venta automático (closure)


def crear_generador_codigos():
    ultimo = 0

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
    subtotales = map(
        lambda item: buscar_por_codigo(inventario, item[0]).precio * item[1],
        caja.items(),
    )
    return reduce(lambda a, b: a + b, subtotales, 0)


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



# ---------- Opción 8: Reportes de ventas (reduce + agregación como parámetro) ----------


def generar_reporte(ventas, agregacion, inicial):
    """Recorre las ventas con reduce, aplicando la función de agregación recibida."""
    return reduce(agregacion, ventas, inicial)


# Funciones de agregación: reciben (acumulado, venta) y devuelven el nuevo acumulado.


def sumar_ingresos(acumulado, venta):
    return acumulado + venta.total


def sumar_unidades(acumulado, venta):
    return acumulado + sum(linea["cantidad"] for linea in venta.lineas)


def unidades_por_producto(acumulado, venta):
    for linea in venta.lineas:
        nombre = linea["nombre"]
        acumulado[nombre] = acumulado.get(nombre, 0) + linea["cantidad"]
    return acumulado


def ingresos_por_producto(acumulado, venta):
    for linea in venta.lineas:
        nombre = linea["nombre"]
        acumulado[nombre] = acumulado.get(nombre, 0) + linea["precio"] * linea["cantidad"]
    return acumulado


def venta_mayor(actual, venta):
    return venta if actual is None or venta.total > actual.total else actual


# Pantallas de cada reporte


def mostrar_resumen_general():
    ingresos = generar_reporte(ventas_registradas, sumar_ingresos, 0)
    unidades = generar_reporte(ventas_registradas, sumar_unidades, 0)
    promedio = ingresos / len(ventas_registradas)

    ui.seccion("Resumen general de ventas")
    ui.tarjetas([
        ("VENTAS", len(ventas_registradas), ui.PRIMARIO),
        ("UNIDADES VENDIDAS", unidades, ui.ACENTO),
        ("INGRESOS", f"S/ {ingresos:.2f}", ui.OK),
        ("TICKET PROMEDIO", f"S/ {promedio:.2f}", ui.PRIMARIO),
    ])


def mostrar_ranking(datos, columna, formato):
    """Tabla {producto: valor} ordenada de mayor a menor."""
    ordenados = sorted(datos.items(), key=lambda par: par[1], reverse=True)
    filas = [
        [posicion, nombre, formato(valor)]
        for posicion, (nombre, valor) in enumerate(ordenados, start=1)
    ]
    ui.tabla(["#", "PRODUCTO", columna], filas, [">", "<", ">"])


def mostrar_unidades_por_producto():
    ui.seccion("Unidades vendidas por producto")
    datos = generar_reporte(ventas_registradas, unidades_por_producto, {})
    mostrar_ranking(datos, "UNIDADES", str)


def mostrar_ingresos_por_producto():
    ui.seccion("Ingresos por producto")
    datos = generar_reporte(ventas_registradas, ingresos_por_producto, {})
    mostrar_ranking(datos, "INGRESOS", lambda valor: f"S/ {valor:.2f}")


def mostrar_venta_mayor():
    ui.seccion("Venta de mayor monto")
    mayor = generar_reporte(ventas_registradas, venta_mayor, None)
    util = ui.ANCHO - 4
    lineas = [ui.par(f"{ui.GRIS}Fecha{ui.RESET}", mayor.fecha, util), None]
    for linea in mayor.lineas:
        izq = f"{linea['nombre']} x{linea['cantidad']}"
        der = f"S/ {linea['precio'] * linea['cantidad']:.2f}"
        lineas.append(ui.par(izq, der, util))
    lineas += [
        None,
        ui.par(
            f"{ui.BOLD}TOTAL{ui.RESET}",
            f"{ui.BOLD}{ui.OK}S/ {mayor.total:.2f}{ui.RESET}",
            util,
        ),
    ]
    ui.caja(lineas, f"Venta #{mayor.codigo:03d}")


def mostrar_historial():
    ui.seccion("Historial de ventas")
    filas = [
        [f"#{v.codigo:03d}", v.fecha, len(v.lineas), f"S/ {v.total:.2f}"]
        for v in ventas_registradas
    ]
    ui.tabla(["N.", "FECHA", "PRODUCTOS", "TOTAL"], filas, ["<", "<", ">", ">"])


# Opción 8 del menú


def reportes_ventas():
    ui.seccion("Reportes de ventas")

    if not ventas_registradas:
        ui.mensaje_aviso("Aún no hay ventas registradas. Registra una en la opción 4.")
        return

    while True:
        ui.seccion("¿Qué reporte deseas ver?")
        ui.opciones([
            ("1", "Resumen general"),
            ("2", "Unidades vendidas por producto"),
            ("3", "Ingresos por producto"),
            ("4", "Venta de mayor monto"),
            ("5", "Historial de ventas"),
            ("0", "Volver al menú"),
        ])
        opcion = ui.pedir("Elige una opción: ")

        if opcion == "1":
            mostrar_resumen_general()
        elif opcion == "2":
            mostrar_unidades_por_producto()
        elif opcion == "3":
            mostrar_ingresos_por_producto()
        elif opcion == "4":
            mostrar_venta_mayor()
        elif opcion == "5":
            mostrar_historial()
        elif opcion == "0":
            return
        else:
            ui.mensaje_error("Opción inválida.")
