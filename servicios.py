from modelos import CATEGORIAS, Accesorio, Equipo, EquipoReacondicionado

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


def pedir_categoria():
    """Muestra las categorías (tupla) y devuelve la tupla elegida."""
    print("\nCategoría:")
    for numero, (_, nombre) in enumerate(CATEGORIAS, start=1):
        print(f"  {numero}. {nombre}")

    while True:
        opcion = input(f"Elige la categoría (1-{len(CATEGORIAS)}): ").strip()
        if opcion.isdigit() and 1 <= int(opcion) <= len(CATEGORIAS):
            return CATEGORIAS[int(opcion) - 1]
        print("  Error: opción inválida.")


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
    categoria = pedir_categoria()

    datos = {
        "codigo": codigo,
        "nombre": nombre,
        "precio": precio,
        "stock": stock,
        "categoria": categoria,
    }

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
    grupos = inventario.agrupar_por_categoria()  # {categoria: [productos]}

    if not grupos:
        print("No hay productos registrados todavía.")
        return

    for categoria, productos in grupos.items():
        print(f"\n[{categoria}] ({len(productos)})")
        for p in productos:
            print(f"  {p.descripcion()}")  # polimorfismo: cada clase muestra distinto

    total = sum(len(productos) for productos in grupos.values())
    print(f"\nTotal: {total} producto(s) en {len(grupos)} categoría(s)")


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


def reponer_stock(inventario):
    print("\n--- REPONER STOCK ---")
    productos = inventario.listar()

    if not productos:
        print("No hay productos registrados todavía.")
        return

    print("Productos actuales:")
    for p in productos:
        print(f"  {p.codigo} - {p.nombre} | Stock actual: {p.stock}")

    codigo = leer_texto("\nCódigo del producto a reponer: ").upper()
    coincidencias = list(filter(lambda p: p.codigo == codigo, productos))

    if not coincidencias:
        print("  Error: código no encontrado.")
        return

    producto = coincidencias[0]
    print(f"  Producto: {producto.nombre} | Stock actual: {producto.stock}")

    while True:
        cantidad = leer_entero("Cantidad a agregar: ")
        if cantidad > 0:
            break
        print("  Error: la cantidad debe ser mayor a 0.")

    producto.stock += cantidad
    print(f"\nStock repuesto correctamente. "
          f"'{producto.nombre}' ahora tiene {producto.stock} unidad(es).")


# ---------- Opción 7: Detectar stock bajo (closure) ----------

def crear_filtro_stock_bajo(limite):
    """Closure: recuerda el límite mínimo de stock para evaluar cada producto."""
    def tiene_stock_bajo(producto):
        return producto.stock < limite

    return tiene_stock_bajo


def detectar_stock_bajo(inventario):
    print("\n--- DETECTAR STOCK BAJO ---")
    productos = inventario.listar()

    if not productos:
        print("No hay productos registrados todavía.")
        return

    limite = leer_entero("Mostrar productos con stock menor a (ej: 5): ")
    es_stock_bajo = crear_filtro_stock_bajo(limite)
    bajos = list(filter(es_stock_bajo, productos))

    print(f"\n--- STOCK BAJO (menos de {limite} unidades) ---")
    if not bajos:
        print("Todos los productos tienen stock suficiente.")
        return

    for p in bajos:
        print(f"  ({p.tipo()}) {p.descripcion()}")
    print(f"\nTotal con stock bajo: {len(bajos)} producto(s)")
