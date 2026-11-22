# Categorías disponibles: tupla de tuplas (id, nombre). Son inmutables.
CATEGORIAS = (
    ("PER", "Periféricos"),
    ("ENE", "Cargadores y energía"),
    ("PRO", "Fundas y protección"),
    ("LAP", "Laptops"),
    ("CEL", "Celulares y tablets"),
    ("OTR", "Otros"),
)

CATEGORIA_POR_DEFECTO = CATEGORIAS[-1]  # ("OTR", "Otros")


def obtener_categoria(id_categoria):
    """Devuelve la tupla (id, nombre) de la categoría, o la de por defecto."""
    for categoria in CATEGORIAS:
        if categoria[0] == id_categoria:
            return categoria
    return CATEGORIA_POR_DEFECTO


class Producto:
    """Clase base para todos los productos de la tienda."""

    def __init__(self, codigo, nombre, precio, stock, categoria=CATEGORIA_POR_DEFECTO):
        self.codigo = codigo
        self.nombre = nombre
        self.precio = precio
        self.stock = stock
        self.categoria = categoria  # tupla (id, nombre)

    def descripcion(self):
        return (
            f"[{self.codigo}] {self.nombre} - S/ {self.precio:.2f} | "
            f"Stock: {self.stock} | Categoría: {self.categoria[1]}"
        )

    def tipo(self):
        return "General"


class Reacondicionado:
    """Clase auxiliar: aporta los meses de uso previo del equipo."""

    def __init__(self, meses_uso=0, **kwargs):
        super().__init__(**kwargs)
        self.meses_uso = meses_uso


# Herencia simple
class Accesorio(Producto):
    def __init__(self, compatible_con="Universal", **kwargs):
        super().__init__(**kwargs)
        self.compatible_con = compatible_con

    def descripcion(self):  # polimorfismo
        return super().descripcion() + f" | Compatible con: {self.compatible_con}"

    def tipo(self):
        return "Accesorio"


# Herencia simple
class Equipo(Producto):
    def __init__(self, meses_garantia=0, **kwargs):
        super().__init__(**kwargs)
        self.meses_garantia = meses_garantia

    def descripcion(self):  # polimorfismo
        return super().descripcion() + f" | Garantía: {self.meses_garantia} meses"

    def tipo(self):
        return "Equipo"


# Herencia múltiple donde hereda de Reacondicionado y de Equipo
class EquipoReacondicionado(Reacondicionado, Equipo):
    def descripcion(self):  # polimorfismo
        return super().descripcion() + f" | Uso previo: {self.meses_uso} meses"

    def tipo(self):
        return "Equipo reacondicionado"


class Inventario:
    """Maneja los productos en un diccionario {codigo: producto}."""

    def __init__(self):
        self.productos = {}

    def agregar(self, producto):
        self.productos[producto.codigo] = producto

    def existe_codigo(self, codigo):
        return codigo in self.productos

    def obtener(self, codigo):
        """Devuelve el producto con ese código, o None si no existe."""
        return self.productos.get(codigo)

    def listar(self):
        return list(self.productos.values())

    def agrupar_por_categoria(self):
        """Devuelve un diccionario {nombre_categoria: [productos]}."""
        grupos = {}
        for p in self.productos.values():
            grupos.setdefault(p.categoria[1], []).append(p)
        return grupos