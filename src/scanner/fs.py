import os
from pathlib import Path

def escanear_roms(ruta_raiz: str, extensiones: set, recursivo: bool = True) -> list:
    roms = []
    base = Path(ruta_raiz)
    if not base.exists():
        return roms
    if recursivo:
        for root, _, files in os.walk(base):
            for f in files:
                if Path(f).suffix.lower() in extensiones:
                    roms.append(str(Path(root) / f))
    else:
        for f in os.listdir(base):
            if Path(f).suffix.lower() in extensiones:
                roms.append(str(base / f))
    return roms

def obtener_arbol_directorios(ruta_raiz: str) -> dict:
    return _construir_arbol(ruta_raiz, ruta_raiz)

def _construir_arbol(ruta_actual: str, ruta_raiz: str) -> dict:
    nombre = _obtener_nombre_relativo(ruta_actual, ruta_raiz)
    hijos = _obtener_subdirectorios(ruta_actual, ruta_raiz)
    archivos = _obtener_archivos_directos(ruta_actual)
    return {"nombre": nombre, "ruta": ruta_actual, "hijos": hijos, "archivos": archivos}

def _obtener_nombre_relativo(ruta_actual: str, ruta_raiz: str) -> str:
    nombre_rel = os.path.relpath(ruta_actual, ruta_raiz)
    return nombre_rel if nombre_rel != "." else os.path.basename(ruta_raiz)

def _obtener_subdirectorios(ruta_actual: str, ruta_raiz: str) -> list:
    hijos = []
    for elemento in os.listdir(ruta_actual):
        ruta_completa = os.path.join(ruta_actual, elemento)
        if os.path.isdir(ruta_completa):
            hijos.append(_construir_arbol(ruta_completa, ruta_raiz))
    return hijos

def _obtener_archivos_directos(ruta_actual: str) -> list:
    archivos = []
    for elemento in os.listdir(ruta_actual):
        ruta_completa = os.path.join(ruta_actual, elemento)
        if os.path.isfile(ruta_completa):
            archivos.append(ruta_completa)
    return archivos