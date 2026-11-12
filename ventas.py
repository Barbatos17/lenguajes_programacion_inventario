from datetime import datetime
from functools import reduce
from servicios import leer_texto, leer_entero


#Código de venta automático (closure)

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
        return (f"Venta #{self.codigo} | {self.fecha} | "
                f"{len(self.lineas)} producto(s) | Total: S/ {self.total:.2f}")


# Lista donde se guardan las ventas confirmadas (en memoria, sin base de datos)
ventas_registradas = []


# Funciones de apoyo

def buscar_por_codigo(inventario, codigo):
    """Devuelve el producto con ese código, o None si no existe."""
    coincidencias = list(filter(lambda p: p.codigo == codigo, inventario.listar()))
    return coincidencias[0] if coincidencias else None


def mostrar_productos_disponibles(inventario):
    """Muestra solo los productos con stock mayor a 0."""
    disponibles = list(filter(lambda p: p.stock > 0, inventario.listar()))
    print("\n--- PRODUCTOS DISPONIBLES ---")
    if not disponibles:
        print("No hay productos con stock.")
    for p in disponibles:
        print(p.descripcion())
    return disponibles


def calcular_total(inventario, caja):
    """Suma precio x cantidad de cada producto de la caja (map + reduce)."""
    subtotales = map(
        lambda item: buscar_por_codigo(inventario, item[0]).precio * item[1],
        caja.items()
    )
    return reduce(lambda a, b: a + b, subtotales, 0)


def mostrar_resumen(inventario, caja):
    print("\n--- RESUMEN DE LA VENTA ---")
    if not caja:
        print("La caja está vacía.")
        return
    for codigo, cantidad in caja.items():
        p = buscar_por_codigo(inventario, codigo)
        print(f"  [{codigo}] {p.nombre} x {cantidad} = S/ {p.precio * cantidad:.2f}")
    print(f"  TOTAL: S/ {calcular_total(inventario, caja):.2f}")


#  La caja (diccionario {codigo: cantidad}) 

def pedir_producto(inventario, caja):
    """Pide código y cantidad, valida y agrega a la caja."""
    codigo = leer_texto("\nCódigo del producto: ").upper()
    producto = buscar_por_codigo(inventario, codigo)

    if producto is None:
        print("  Error: código no encontrado.")
        return

    if producto.stock == 0:
        print("  Advertencia: ese producto no tiene stock.")
        return

    ya_en_caja = caja.get(codigo, 0)
    disponible = producto.stock - ya_en_caja
    print(f"  Disponible para agregar: {disponible}")

    cantidad = leer_entero("Cantidad: ")
    if cantidad == 0:
        print("  Error: la cantidad debe ser mayor a 0.")
        return

    if ya_en_caja + cantidad > producto.stock:
        print(f"  Advertencia: stock no disponible. "
              f"Solo puedes agregar {disponible} unidad(es) de '{producto.nombre}'.")
        return

    caja[codigo] = ya_en_caja + cantidad
    print(f"  Agregado: {producto.nombre} x {cantidad}")


def quitar_producto(caja):
    """Quita un producto de la caja."""
    if not caja:
        print("  La caja está vacía.")
        return
    codigo = leer_texto("Código del producto a quitar: ").upper()
    if codigo in caja:
        del caja[codigo]
        print(f"  Producto {codigo} quitado de la caja.")
    else:
        print("  Error: ese producto no está en la caja.")


# Confirmar la venta 

def confirmar_venta(inventario, caja):
    """Descuenta el stock, crea la Venta y la guarda."""
    lineas = []
    for codigo, cantidad in caja.items():
        p = buscar_por_codigo(inventario, codigo)
        p.stock -= cantidad
        lineas.append({
            "codigo": codigo,
            "nombre": p.nombre,
            "cantidad": cantidad,
            "precio": p.precio,
        })

    total = sum(map(lambda l: l["precio"] * l["cantidad"], lineas))
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    venta = Venta(generar_codigo(), fecha, lineas, total)
    ventas_registradas.append(venta)
    return venta


# Opción 4 del menú

def registrar_venta(inventario):
    print("\n--- REGISTRAR VENTA ---")
    caja = {}

    mostrar_productos_disponibles(inventario)

    while True:
        print("\n¿Qué deseas hacer?")
        print("  1. Agregar producto")
        print("  2. Quitar producto")
        print("  3. Terminar y ver resumen")
        print("  0. Cancelar venta")
        opcion = input("Elige una opción: ").strip()

        if opcion == "1":
            pedir_producto(inventario, caja)
        elif opcion == "2":
            quitar_producto(caja)
        elif opcion == "3":
            if not caja:
                print("  Error: no hay productos en la caja.")
                continue
            mostrar_resumen(inventario, caja)
            respuesta = leer_texto("\n¿Confirmar venta? (s/n): ").lower()
            if respuesta == "s":
                venta = confirmar_venta(inventario, caja)
                print(f"\nVenta #{venta.codigo} registrada. "
                      f"Total: S/ {venta.total:.2f}")
                return
            print("  Aún puedes seguir editando la caja.")
        elif opcion == "0":
            print("\nVenta cancelada. El stock no cambió.")
            return
        else:
            print("  Error: opción inválida.")