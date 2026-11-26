import json
import os

import ventas
from modelos import (
    Accesorio,
    Equipo,
    EquipoReacondicionado,
    Producto,
    obtener_categoria,
)

ARCHIVO_DATOS = "datos.json"


def _serializar_producto(p):
    data = {
        "tipo": p.tipo(),
        "codigo": p.codigo,
        "nombre": p.nombre,
        "precio": p.precio,
        "stock": p.stock,
        "categoria_id": p.categoria[0],
    }
    if isinstance(p, Accesorio):
        data["compatible_con"] = p.compatible_con
    elif isinstance(p, EquipoReacondicionado):
        data["meses_garantia"] = p.meses_garantia
        data["meses_uso"] = p.meses_uso
    elif isinstance(p, Equipo):
        data["meses_garantia"] = p.meses_garantia
    return data


def _deserializar_producto(d):
    base = {
        "codigo": d["codigo"],
        "nombre": d["nombre"],
        "precio": float(d["precio"]),
        "stock": int(d["stock"]),
        "categoria": obtener_categoria(d.get("categoria_id", "OTR")),
    }
    tipo = d.get("tipo")
    if tipo == "Accesorio":
        return Accesorio(compatible_con=d.get("compatible_con", "Universal"), **base)
    if tipo == "Equipo reacondicionado":
        return EquipoReacondicionado(
            meses_garantia=int(d.get("meses_garantia", 0)),
            meses_uso=int(d.get("meses_uso", 0)),
            **base,
        )
    if tipo == "Equipo":
        return Equipo(meses_garantia=int(d.get("meses_garantia", 0)), **base)
    return Producto(**base)


def guardar_datos(inventario, ruta=ARCHIVO_DATOS):
    """Guarda el inventario y las ventas registradas en un archivo JSON."""
    payload = {
        "productos": [_serializar_producto(p) for p in inventario.listar()],
        "ventas": [
            {
                "codigo": v.codigo,
                "fecha": v.fecha,
                "lineas": v.lineas,
                "total": v.total,
            }
            for v in ventas.ventas_registradas
        ],
    }
    with open(ruta, mode="w", encoding="utf-8") as archivo:
        json.dump(payload, archivo, indent=2, ensure_ascii=False)


def cargar_datos(inventario, ruta=ARCHIVO_DATOS):
    """Carga productos y ventas desde JSON. Devuelve True si existía el archivo."""
    if not os.path.exists(ruta):
        return False

    with open(ruta, mode="r", encoding="utf-8") as archivo:
        payload = json.load(archivo)

    for item in payload.get("productos", []):
        inventario.agregar(_deserializar_producto(item))

    ventas.ventas_registradas.clear()
    ultimo_codigo = 0
    for v in payload.get("ventas", []):
        venta = ventas.Venta(
            codigo=v["codigo"],
            fecha=v["fecha"],
            lineas=v["lineas"],
            total=float(v["total"]),
        )
        ventas.ventas_registradas.append(venta)
        ultimo_codigo = max(ultimo_codigo, venta.codigo)

    # Sincroniza el closure generador de códigos de venta
    ventas.generar_codigo = ventas.crear_generador_codigos(ultimo_codigo)
    return True