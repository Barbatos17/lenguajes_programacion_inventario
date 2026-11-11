class Producto:
    """Clase base para todos los productos de la tienda."""

    def __init__(self, codigo, nombre, precio, stock):
        self.codigo = codigo
        self.nombre = nombre
        self.precio = precio
        self.stock = stock

    def descripcion(self):
        return f"[{self.codigo}] {self.nombre} - S/ {self.precio:.2f} | Stock: {self.stock}"

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
    """Maneja la lista de productos."""

    def __init__(self):
        self.productos = []

    def agregar(self, producto):
        self.productos.append(producto)

    def existe_codigo(self, codigo):
        return any(p.codigo == codigo for p in self.productos)

    def listar(self):
        return self.productos