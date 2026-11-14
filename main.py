import servicios
import ventas
from modelos import Accesorio, Equipo, EquipoReacondicionado, Inventario

def cargar_datos_ejemplo(inventario):
    """Carga productos de ejemplo para poder probar el sistema."""
    inventario.agregar(Accesorio(
        codigo="A01", nombre="Mouse Logitech M170", precio=39.9, stock=25,
        compatible_con="PC y laptop"))
    inventario.agregar(Accesorio(
        codigo="A02", nombre="Cargador USB-C 65W", precio=79.0, stock=15,
        compatible_con="Laptop y celular"))
    inventario.agregar(Accesorio(
        codigo="A03", nombre="Funda para laptop 15 pulgadas", precio=45.0, stock=10,
        compatible_con="Laptop 15 pulgadas"))
    inventario.agregar(Equipo(
        codigo="E01", nombre="Laptop Lenovo IdeaPad 3", precio=2199.0, stock=6,
        meses_garantia=12))
    inventario.agregar(Equipo(
        codigo="E02", nombre="Samsung Galaxy A15", precio=799.0, stock=9,
        meses_garantia=12))
    inventario.agregar(EquipoReacondicionado(
        codigo="R01", nombre="Laptop HP ProBook reacondicionada", precio=1299.0, stock=3,
        meses_garantia=6, meses_uso=18))


def mostrar_menu():
    print("\n==============================================")
    print("   TIENDA DE TECNOLOGÍA - INVENTARIO Y VENTAS")
    print("==============================================")
    print("1. Registrar producto")
    print("2. Listar productos")
    print("3. Buscar producto")
    print("4. Registrar venta")
    print("5. Reponer stock")
    print("6. Ordenar productos")
    print("7. Detectar stock bajo")
    print("8. Reportes de ventas")
    print("0. Salir")
    print("----------------------------------------------")


def proximamente():
    print("\nEsta opción estará disponible en el siguiente avance.")


def main():
    inventario = Inventario()
    cargar_datos_ejemplo(inventario)

    while True:
        mostrar_menu()
        opcion = input("Elige una opción: ").strip()

        if opcion == "1":
            servicios.registrar_producto(inventario)
        elif opcion == "2":
            servicios.listar_productos(inventario)
        elif opcion == "3":
            servicios.buscar_producto(inventario)
        elif opcion == "4":
            ventas.registrar_venta(inventario)
        elif opcion in ("5", "6", "7", "8"):
            proximamente()
        elif opcion == "0":
            print("\nHasta luego.")
            break
        else:
            print("\n  Error: opción inválida, intenta de nuevo.")


if __name__ == "__main__":
    main()