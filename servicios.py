from modelos import Accesorio, Equipo, EquipoReacondicionado

# ---------- Entrada de datos con validación ----------

def leer_texto(mensaje):
    """Pide un texto que no esté vacío."""
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print("  Error: no puede estar vacío.")


def leer_decimal(mensaje):
    """Pide un número decimal no negativo."""
    while True:
        try:
            valor = float(input(mensaje))
            if valor < 0:
                print("  Error: no puede ser negativo.")
                continue
            return valor
        except ValueError:
            print("  Error: escribe un número válido.")


def leer_entero(mensaje):
    """Pide un número entero no negativo."""
    while True:
        try:
            valor = int(input(mensaje))
            if valor < 0:
                print("  Error: no puede ser negativo.")
                continue
            return valor
        except ValueError:
            print("  Error: escribe un número entero válido.")


def pedir_codigo_nuevo(inventario, ejemplo="A01"):
    """Pide un código que todavía no exista en el inventario."""
    while True:
        codigo = leer_texto(f"Código (ej: {ejemplo}): ").upper()
        if inventario.existe_codigo(codigo):
            print("  Error: ese código ya existe, prueba con otro.")
        else:
            return codigo


# ---------- Opciones del menú ----------

def registrar_producto(inventario):
    print("\n--- REGISTRAR PRODUCTO ---")
    print("Tipo de producto:")
    print("  1. Accesorio (mouse, cargador, funda)")
    print("  2. Equipo (laptop, celular, tablet)")
    print("  3. Equipo reacondicionado")

    while True:
        tipo = input("Elige el tipo (1-3): ").strip()
        if tipo in ("1", "2", "3"):
            break
        print("  Error: opción inválida.")

    ejemplos = {"1": "A01", "2": "E01", "3": "R01"}
    codigo = pedir_codigo_nuevo(inventario, ejemplos[tipo])
    nombre = leer_texto("Nombre: ")
    precio = leer_decimal("Precio (S/): ")
    stock = leer_entero("Stock inicial: ")

    datos = {"codigo": codigo, "nombre": nombre, "precio": precio, "stock": stock}

    if tipo == "1":
        datos["compatible_con"] = leer_texto("Compatible con (ej: PC, Android, Universal): ")
        producto = Accesorio(**datos)
    elif tipo == "2":
        datos["meses_garantia"] = leer_entero("Meses de garantía: ")
        producto = Equipo(**datos)
    else:
        datos["meses_garantia"] = leer_entero("Meses de garantía: ")
        datos["meses_uso"] = leer_entero("Meses de uso previo: ")
        producto = EquipoReacondicionado(**datos)

    inventario.agregar(producto)
    print(f"\nProducto '{nombre}' registrado correctamente.")


def listar_productos(inventario):
    print("\n--- LISTA DE PRODUCTOS ---")
    productos = inventario.listar()

    if not productos:
        print("No hay productos registrados todavía.")
        return

    for p in productos:
        print(p.descripcion())  # polimorfismo: cada clase muestra distinto
    print(f"\nTotal: {len(productos)} producto(s)")


def buscar_producto(inventario):
    print("\n--- BUSCAR PRODUCTO ---")
    productos = inventario.listar()

    if not productos:
        print("No hay productos registrados todavía.")
        return

    print("Productos disponibles:")
    for p in productos:
        print(f"  {p.codigo} - {p.nombre}")

    texto = leer_texto("\nEscribe el código o parte del nombre: ").lower()

    encontrados = [
        p for p in productos
        if texto == p.codigo.lower() or texto in p.nombre.lower()
    ]

    if not encontrados:
        print("  Error: no se encontró ningún producto con ese dato.")
        return

    print(f"\nResultados ({len(encontrados)}):")
    for p in encontrados:
        print(f"  ({p.tipo()}) {p.descripcion()}")