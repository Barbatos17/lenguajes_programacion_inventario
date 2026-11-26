import textwrap

import ui
from modelos import CATEGORIAS, Accesorio, Equipo, EquipoReacondicionado


def mostrar_tabla_productos(productos, limite=5):
    """Tabla estándar de productos (la usan servicios.py y ventas.py)."""
    filas = [
        [
            f"{ui.ACENTO}{p.codigo}{ui.RESET}",
            p.nombre,
            ui.etiqueta_tipo(p.tipo()),
            f"S/ {p.precio:.2f}",
            ui.nivel_stock(p.stock, limite),
        ]
        for p in productos
    ]
    ui.tabla(
        ["CÓDIGO", "NOMBRE", "TIPO", "PRECIO", "STOCK"],
        filas,
        ["<", "<", "<", ">", "<"],
    )


# ---------- Entrada de datos con validación ----------


def leer_texto(mensaje):
    """Pide un texto que no esté vacío."""
    while True:
        valor = ui.pedir(mensaje)
        if valor:
            return valor
        ui.mensaje_error("No puede estar vacío.")


def leer_decimal(mensaje):
    """Pide un número decimal no negativo."""
    while True:
        try:
            valor = float(ui.pedir(mensaje))
            if valor < 0:
                ui.mensaje_error("No puede ser negativo.")
                continue
            return valor
        except ValueError:
            ui.mensaje_error("Escribe un número válido.")


def leer_entero(mensaje):
    """Pide un número entero no negativo."""
    while True:
        try:
            valor = int(ui.pedir(mensaje))
            if valor < 0:
                ui.mensaje_error("No puede ser negativo.")
                continue
            return valor
        except ValueError:
            ui.mensaje_error("Escribe un número entero válido.")


def pedir_codigo_nuevo(inventario, ejemplo="A01"):
    """Pide un código que todavía no exista en el inventario."""
    while True:
        codigo = leer_texto(f"Código (ej: {ejemplo}): ").upper()
        if inventario.existe_codigo(codigo):
            ui.mensaje_error("Ese código ya existe, prueba con otro.")
        else:
            return codigo


def pedir_categoria():
    """Muestra las categorías (tupla) y devuelve la tupla elegida."""
    ui.seccion("Categoría")
    ui.opciones(
        [(str(numero), nombre) for numero, (_, nombre) in enumerate(CATEGORIAS, start=1)]
    )

    while True:
        opcion = ui.pedir(f"Elige la categoría (1-{len(CATEGORIAS)}): ")
        if opcion.isdigit() and 1 <= int(opcion) <= len(CATEGORIAS):
            return CATEGORIAS[int(opcion) - 1]
        ui.mensaje_error("Opción inválida.")


# ---------- Opciones del menú ----------


def registrar_producto(inventario):
    ui.seccion("Registrar producto")
    ui.opciones([
        ("1", "Accesorio (mouse, cargador, funda)"),
        ("2", "Equipo (laptop, celular, tablet)"),
        ("3", "Equipo reacondicionado"),
    ])

    while True:
        tipo = ui.pedir("Elige el tipo (1-3): ")
        if tipo in ("1", "2", "3"):
            break
        ui.mensaje_error("Opción inválida.")

    ejemplos = {"1": "A01", "2": "E01", "3": "R01"}
    print()
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

    print()
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

    ui.seccion("Producto registrado")
    mostrar_tabla_productos([producto])
    print()
    ui.mensaje_ok(f"Producto '{nombre}' registrado correctamente.")


def listar_productos(inventario):
    grupos = inventario.agrupar_por_categoria()  # {categoria: [productos]}

    if not grupos:
        ui.seccion("Lista de productos")
        ui.mensaje_aviso("No hay productos registrados todavía.")
        return

    for categoria, productos in grupos.items():
        ui.seccion(f"{categoria} ({len(productos)})")
        mostrar_tabla_productos(productos)

    todos = inventario.listar()
    unidades = sum(p.stock for p in todos)
    valor = sum(p.precio * p.stock for p in todos)

    ui.seccion("Resumen del inventario")
    ui.tarjetas([
        ("PRODUCTOS", len(todos), ui.PRIMARIO),
        ("CATEGORÍAS", len(grupos), ui.ACENTO),
        ("UNIDADES", unidades, ui.PRIMARIO),
        ("VALOR INVENTARIO", f"S/ {valor:,.2f}", ui.OK),
    ])
    print()
    ui.mensaje_ok("Lista generada correctamente en la consola.")


def buscar_producto(inventario):
    ui.seccion("Buscar producto")
    productos = inventario.listar()

    if not productos:
        ui.mensaje_aviso("No hay productos registrados todavía.")
        return

    mostrar_tabla_productos(productos)

    texto = leer_texto("\nEscribe el código o parte del nombre: ")

    # Usa la sobrecarga de Inventario.buscar (versión para str)
    encontrados = inventario.buscar(texto)

    if not encontrados:
        ui.mensaje_error("No se encontró ningún producto con ese dato.")
        return

    ui.seccion(f"Resultados ({len(encontrados)})")
    for p in encontrados:
        # polimorfismo: cada clase arma su propia descripción
        lineas = textwrap.wrap(p.descripcion(), ui.ANCHO - 4)
        ui.caja(lineas, f"{p.codigo} - detalle")


def reponer_stock(inventario):
    ui.seccion("Reponer stock")
    productos = inventario.listar()

    if not productos:
        ui.mensaje_aviso("No hay productos registrados todavía.")
        return

    mostrar_tabla_productos(productos)

    codigo = leer_texto("\nCódigo del producto a reponer: ").upper()
    coincidencias = list(filter(lambda p: p.codigo == codigo, productos))

    if not coincidencias:
        ui.mensaje_error("Código no encontrado.")
        return

    producto = coincidencias[0]
    ui.mensaje_info(f"{producto.nombre} | Stock actual: {producto.stock}")

    while True:
        cantidad = leer_entero("Cantidad a agregar: ")
        if cantidad > 0:
            break
        ui.mensaje_error("La cantidad debe ser mayor a 0.")

    producto.stock += cantidad
    print()
    ui.mensaje_ok(
        f"Stock repuesto correctamente. "
        f"'{producto.nombre}' ahora tiene {producto.stock} unidad(es)."
    )

    # ---------- Opción 6: Ordenar productos (lambda) ----------


def ordenar_productos(inventario):
    ui.seccion("Ordenar productos")
    productos = inventario.listar()

    if not productos:
        ui.mensaje_aviso("No hay productos registrados todavía.")
        return

    criterios = {
        "1": ("Precio (menor a mayor)", lambda p: p.precio, False),
        "2": ("Precio (mayor a menor)", lambda p: p.precio, True),
        "3": ("Stock (menor a mayor)", lambda p: p.stock, False),
        "4": ("Stock (mayor a menor)", lambda p: p.stock, True),
        "5": ("Nombre (A - Z)", lambda p: p.nombre.lower(), False),
        "6": ("Categoría (A - Z)", lambda p: p.categoria[1].lower(), False),
    }

    ui.opciones([(k, desc) for k, (desc, _, _) in criterios.items()])

    while True:
        opcion = ui.pedir("\nElige el criterio de ordenamiento (1-6): ")
        if opcion in criterios:
            break
        ui.mensaje_error("Opción inválida.")

    etiqueta, clave_orden, inverso = criterios[opcion]
    ordenados = sorted(productos, key=clave_orden, reverse=inverso)

    ui.seccion(f"Productos ordenados por {etiqueta}")
    mostrar_tabla_productos(ordenados)
    print()
    ui.mensaje_ok(f"Se ordenaron {len(ordenados)} producto(s) por {etiqueta.lower()}.")

# ---------- Opción 7: Detectar stock bajo (closure) ----------


def crear_filtro_stock_bajo(limite):
    """Closure: recuerda el límite mínimo de stock para evaluar cada producto."""
    def tiene_stock_bajo(producto):
        return producto.stock < limite

    return tiene_stock_bajo


def detectar_stock_bajo(inventario):
    ui.seccion("Detectar stock bajo")
    productos = inventario.listar()

    if not productos:
        ui.mensaje_aviso("No hay productos registrados todavía.")
        return

    limite = leer_entero("Mostrar productos con stock menor a (ej: 5): ")
    es_stock_bajo = crear_filtro_stock_bajo(limite)
    bajos = list(filter(es_stock_bajo, productos))

    ui.seccion(f"Stock bajo (menos de {limite} unidades)")
    if not bajos:
        ui.mensaje_ok("Todos los productos tienen stock suficiente.")
        return

    mostrar_tabla_productos(bajos, limite)
    print()
    ui.mensaje_aviso(f"Total con stock bajo: {len(bajos)} producto(s)")