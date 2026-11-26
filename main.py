import servicios
import ui
import persistencia
import ventas
from modelos import (
    Accesorio,
    Equipo,
    EquipoReacondicionado,
    Inventario,
    obtener_categoria,
)

LIMITE_STOCK_BAJO = 5


def cargar_datos_ejemplo(inventario):
    """Carga productos de ejemplo para poder probar el sistema."""
    inventario.agregar(Accesorio(
        codigo="A01", categoria=obtener_categoria("PER"), nombre="Mouse Logitech M170", precio=39.9, stock=25,
        compatible_con="PC y laptop"))
    inventario.agregar(Accesorio(
        codigo="A02", categoria=obtener_categoria("ENE"), nombre="Cargador USB-C 65W", precio=79.0, stock=15,
        compatible_con="Laptop y celular"))
    inventario.agregar(Accesorio(
        codigo="A03", categoria=obtener_categoria("PRO"), nombre="Funda para laptop 15 pulgadas", precio=45.0, stock=10,
        compatible_con="Laptop 15 pulgadas"))
    inventario.agregar(Equipo(
        codigo="E01", categoria=obtener_categoria("LAP"), nombre="Laptop Lenovo IdeaPad 3", precio=2199.0, stock=6,
        meses_garantia=12))
    inventario.agregar(Equipo(
        codigo="E02", categoria=obtener_categoria("CEL"), nombre="Samsung Galaxy A15", precio=799.0, stock=9,
        meses_garantia=12))
    inventario.agregar(EquipoReacondicionado(
        codigo="R01", categoria=obtener_categoria("LAP"), nombre="Laptop HP ProBook reacondicionada", precio=1299.0, stock=3,
        meses_garantia=6, meses_uso=18))


def mostrar_pantalla_principal(inventario):
    productos = inventario.listar()
    unidades = sum(p.stock for p in productos)
    ingresos = sum(v.total for v in ventas.ventas_registradas)
    bajos = [p for p in productos if p.stock < LIMITE_STOCK_BAJO]

    ui.limpiar()
    ui.banner()
    print()
    ui.tarjetas([
        ("PRODUCTOS", len(productos), ui.PRIMARIO),
        ("UNIDADES EN STOCK", unidades, ui.ACENTO),
        ("VENTAS", len(ventas.ventas_registradas), ui.PRIMARIO),
        ("INGRESOS", f"S/ {ingresos:.2f}", ui.OK),
    ])
    if bajos:
        print()
        ui.mensaje_aviso(
            f"{len(bajos)} producto(s) con stock bajo. Revisa la opción 7."
        )
    print()
    ui.menu([
        ("1", "Registrar producto", "Agregar al inventario"),
        ("2", "Listar productos", "Ver por categoría"),
        ("3", "Buscar producto", "Por código o nombre"),
        ("4", "Registrar venta", "Caja y comprobante"),
        ("5", "Reponer stock", "Sumar unidades"),
        ("6", "Ordenar productos", "Por precio, stock o nombre"),
        ("7", "Detectar stock bajo", "Alerta de reposición"),
        ("8", "Reportes de ventas", "Resumen en consola y CSV"),
        ("9", "Inventario CSV", "Exportar o importar"),
        None,
        ("0", "Salir del sistema", "Cerrar el programa"),
    ])


def proximamente():
    print()
    ui.mensaje_aviso("Esta opción estará disponible en el siguiente avance.")


def main():
    inventario = Inventario()

    if persistencia.cargar_datos(inventario):
        ui.cargando("Cargando datos desde datos.json", 0.8)
    else:
        cargar_datos_ejemplo(inventario)
        persistencia.guardar_datos(inventario)
        ui.cargando("Inicializando inventario de ejemplo", 0.8)

    while True:
        mostrar_pantalla_principal(inventario)
        opcion = ui.pedir("\nIngrese una opción: ")

        if opcion == "1":
            servicios.registrar_producto(inventario)
            persistencia.guardar_datos(inventario)
        elif opcion == "2":
            servicios.listar_productos(inventario)
        elif opcion == "3":
            servicios.buscar_producto(inventario)
        elif opcion == "4":
            ventas.registrar_venta(inventario)
            persistencia.guardar_datos(inventario)
        elif opcion == "5":
            servicios.reponer_stock(inventario)
            persistencia.guardar_datos(inventario)
        elif opcion == "6":
            servicios.ordenar_productos(inventario)
        elif opcion == "7":
            servicios.detectar_stock_bajo(inventario)
        elif opcion == "8":
            ventas.reporte_ventas()
        elif opcion == "9":
            servicios.gestionar_csv(inventario)
            persistencia.guardar_datos(inventario)
        elif opcion == "0":
            persistencia.guardar_datos(inventario)
            print()
            ui.mensaje_ok("Datos guardados. Hasta luego.")
            break
        else:
            print()
            ui.mensaje_error("Opción inválida, intenta de nuevo.")

        ui.pausa()




if __name__ == "__main__":
    main()