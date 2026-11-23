import os
import re
import sys
import time
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

os.system("")  # habilita colores ANSI en la terminal de Windows

# ---------- Personalización ----------
NOMBRE_TIENDA = "TECH STORE"
SUBTITULO = "Inventario y control de ventas"
ANCHO = 90


def _rgb(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"


RESET = "\033[0m"
BOLD = "\033[1m"
PRIMARIO = _rgb(0, 174, 255)   # azul eléctrico
ACENTO = _rgb(0, 229, 200)     # verde agua
BORDE = _rgb(0, 110, 170)      # azul oscuro para bordes
OK = _rgb(80, 250, 123)
ERROR = _rgb(255, 85, 85)
AVISO = _rgb(255, 184, 108)
GRIS = _rgb(130, 140, 160)
BLANCO = _rgb(235, 240, 245)


# ---------- Utilidades internas ----------


def _visible(texto):
    """Largo del texto sin contar los códigos de color."""
    return len(re.sub(r"\033\[[0-9;]*m", "", str(texto)))


def _pad(texto, ancho, alinear="<"):
    texto = str(texto)
    falta = max(ancho - _visible(texto), 0)
    if alinear == ">":
        return " " * falta + texto
    if alinear == "^":
        izq = falta // 2
        return " " * izq + texto + " " * (falta - izq)
    return texto + " " * falta


def centrar(texto, ancho=ANCHO):
    return _pad(texto, ancho, "^")


def par(izq, der, ancho):
    """Texto a la izquierda y texto a la derecha en la misma línea."""
    return izq + " " * max(ancho - _visible(izq) - _visible(der), 1) + der


def degradado(texto, c1=(0, 174, 255), c2=(0, 229, 200)):
    n = max(len(texto) - 1, 1)
    salida = ""
    for i, ch in enumerate(texto):
        t = i / n
        r, g, b = (int(c1[k] + (c2[k] - c1[k]) * t) for k in range(3))
        salida += f"{_rgb(r, g, b)}{ch}"
    return salida + RESET


def limpiar():
    os.system("cls" if os.name == "nt" else "clear")


# ---------- Bloques visuales ----------


def banner():
    interior = ANCHO - 2
    titulo = "  ".join(" ".join(palabra) for palabra in NOMBRE_TIENDA.split())
    fecha = datetime.now().strftime("%d/%m/%Y  %H:%M")
    v = f"{BORDE}║{RESET}"

    print(f"{BORDE}╔{'═' * interior}╗{RESET}")
    print(f"{v}{' ' * interior}{v}")
    print(f"{v}{centrar(f'{BOLD}{degradado(titulo)}', interior)}{v}")
    print(f"{v}{centrar(f'{GRIS}{SUBTITULO}{RESET}', interior)}{v}")
    print(f"{v}{' ' * interior}{v}")
    print(f"{BORDE}╠{'═' * interior}╣{RESET}")
    info = par(
        f" {GRIS}Equipos, accesorios y reacondicionados{RESET}",
        f"{GRIS}{fecha} {RESET}",
        interior,
    )
    print(f"{v}{info}{v}")
    print(f"{BORDE}╚{'═' * interior}╝{RESET}")


def seccion(titulo):
    rotulo = f" {titulo.upper()} "
    print()
    print(
        f"{PRIMARIO}▌{RESET}{BOLD}{ACENTO}{rotulo}{RESET}"
        f"{BORDE}{'─' * max(ANCHO - len(rotulo) - 1, 3)}{RESET}"
    )


def caja(lineas, titulo="", ancho=ANCHO, color=BORDE):
    """lineas: lista de textos. Un None dibuja una línea separadora."""
    interior = ancho - 2
    if titulo:
        rotulo = f" {titulo.upper()} "
        print(
            f"{color}┌─{RESET}{BOLD}{ACENTO}{rotulo}{RESET}"
            f"{color}{'─' * (interior - 1 - len(rotulo))}┐{RESET}"
        )
    else:
        print(f"{color}┌{'─' * interior}┐{RESET}")
    for linea in lineas:
        if linea is None:
            print(f"{color}├{'─' * interior}┤{RESET}")
        else:
            print(f"{color}│{RESET} {_pad(linea, interior - 2)} {color}│{RESET}")
    print(f"{color}└{'─' * interior}┘{RESET}")


def tarjetas(items, separacion=2):
    """items: lista de (etiqueta, valor, color). Dibuja tarjetas en una fila."""
    n = len(items)
    ancho_t = (ANCHO - separacion * (n - 1)) // n
    interior = ancho_t - 2
    sep = " " * separacion
    v = f"{BORDE}│{RESET}"

    print(sep.join(f"{BORDE}┌{'─' * interior}┐{RESET}" for _ in items))
    print(sep.join(f"{v}{GRIS}{_pad(e, interior, '^')}{RESET}{v}" for e, _, _ in items))
    print(sep.join(f"{v}{BOLD}{c}{_pad(val, interior, '^')}{RESET}{v}" for _, val, c in items))
    print(sep.join(f"{BORDE}└{'─' * interior}┘{RESET}" for _ in items))


def tabla(encabezados, filas, alinear=None, pie=0):
    """
    encabezados: lista de str
    filas: lista de listas
    alinear: "<", ">" o "^" por columna
    pie: cantidad de filas finales que se separan con una línea (ej: TOTAL)
    """
    n = len(encabezados)
    alinear = alinear or ["<"] * n
    filas = [[str(c) for c in fila] for fila in filas]

    anchos = [
        max([_visible(encabezados[i])] + [_visible(f[i]) for f in filas])
        for i in range(n)
    ]
    v = f"{BORDE}│{RESET}"

    def borde(izq, medio, der):
        return f"{BORDE}{izq}{medio.join('─' * (a + 2) for a in anchos)}{der}{RESET}"

    def fila_txt(celdas, estilo=""):
        cierre = RESET if estilo else ""
        partes = (
            f" {estilo}{_pad(c, anchos[i], alinear[i])}{cierre} "
            for i, c in enumerate(celdas)
        )
        return v + v.join(partes) + v

    print(borde("┌", "┬", "┐"))
    print(fila_txt(encabezados, BOLD + PRIMARIO))
    print(borde("├", "┼", "┤"))

    if not filas:
        total = sum(anchos) + 3 * (n - 1)
        print(f"{v} {GRIS}{_pad('(sin registros)', total, '^')}{RESET} {v}")
    else:
        cuerpo = filas[: len(filas) - pie]
        final = filas[len(filas) - pie:]
        for fila in cuerpo:
            print(fila_txt(fila))
        if final:
            print(borde("├", "┼", "┤"))
            for fila in final:
                print(fila_txt(fila))
    print(borde("└", "┴", "┘"))


# ---------- Mensajes ----------


def _etiqueta(texto, fondo):
    r, g, b = fondo
    return f"\033[48;2;{r};{g};{b}m\033[38;2;10;14;20m{BOLD} {texto:^7} {RESET}"


def mensaje_ok(texto):
    print(f"{_etiqueta('OK', (80, 250, 123))} {texto}")


def mensaje_error(texto):
    print(f"{_etiqueta('ERROR', (255, 85, 85))} {texto}")


def mensaje_aviso(texto):
    print(f"{_etiqueta('AVISO', (255, 184, 108))} {texto}")


def mensaje_info(texto):
    print(f"{_etiqueta('INFO', (0, 174, 255))} {texto}")


# ---------- Menús y entrada ----------


def opciones(lista):
    """lista: tuplas (clave, texto). Para submenús."""
    for item in lista:
        print(f"  {ACENTO}{BOLD}[{item[0]}]{RESET} {item[1]}")


def menu(lista, titulo="Menú principal"):
    """lista: tuplas (clave, texto, descripcion). None dibuja una separación."""
    lineas = []
    for item in lista:
        if item is None:
            lineas.append(None)
            continue
        clave, texto, desc = item
        izq = f"{ACENTO}{BOLD}[{clave}]{RESET} {BLANCO}{texto}{RESET}"
        lineas.append(_pad(izq, 34) + f"{GRIS}{desc}{RESET}")
    caja(lineas, titulo)


def pedir(texto):
    saltos = len(texto) - len(texto.lstrip("\n"))
    if saltos:
        print("\n" * (saltos - 1))
    limpio = texto.lstrip("\n")
    return input(f"{PRIMARIO}{BOLD}>{RESET} {BOLD}{BLANCO}{limpio}{RESET}").strip()


def pausa():
    input(f"\n{GRIS}Presiona ENTER para volver al menú...{RESET}")


def cargando(texto="Procesando", segundos=0.8):
    cuadros = "|/-\\"
    fin = time.time() + segundos
    i = 0
    while time.time() < fin:
        print(
            f"\r{PRIMARIO}[{cuadros[i % 4]}]{RESET} {GRIS}{texto}...{RESET}",
            end="",
            flush=True,
        )
        time.sleep(0.1)
        i += 1
    print("\r" + " " * (len(texto) + 12) + "\r", end="")


# ---------- Formato de datos de productos ----------


def nivel_stock(stock, limite=5, maximo=30, largo=6):
    """Número de stock con barra: rojo si es 0, ámbar si es bajo, verde si está bien."""
    if stock == 0:
        color = ERROR
    elif stock < limite:
        color = AVISO
    else:
        color = OK
    llenos = 0 if stock == 0 else max(1, round(min(stock, maximo) / maximo * largo))
    return (
        f"{color}{stock:>3}{RESET} "
        f"{color}{'█' * llenos}{RESET}{GRIS}{'░' * (largo - llenos)}{RESET}"
    )


def etiqueta_tipo(tipo):
    colores = {"Accesorio": ACENTO, "Equipo": PRIMARIO, "Equipo reacondicionado": AVISO}
    cortos = {"Equipo reacondicionado": "Reacond."}
    return f"{colores.get(tipo, BLANCO)}{cortos.get(tipo, tipo)}{RESET}"