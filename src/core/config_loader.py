import json
import os

def cargar_configuracion(ruta_base, nombre_archivo="config.json"):
    ruta_completa = os.path.join(ruta_base, nombre_archivo)
    resultado = _leer_archivo_json(ruta_completa) if os.path.exists(ruta_completa) else _obtener_configuracion_por_defecto()
    return resultado

def guardar_configuracion(ruta_base, configuracion, nombre_archivo="config.json"):
    ruta_completa = os.path.join(ruta_base, nombre_archivo)
    _escribir_archivo_json(ruta_completa, configuracion)

def actualizar_ruta_por_defecto(ruta_base, configuracion, nueva_ruta):
    configuracion["ruta_por_defecto"] = nueva_ruta
    guardar_configuracion(ruta_base, configuracion)

def _leer_archivo_json(ruta_completa):
    with open(ruta_completa, "r", encoding="utf-8") as archivo:
        contenido = json.load(archivo)
    return contenido

def _escribir_archivo_json(ruta_completa, contenido):
    with open(ruta_completa, "w", encoding="utf-8") as archivo:
        json.dump(contenido, archivo, indent=4, ensure_ascii=False)

def _obtener_configuracion_por_defecto():
    configuracion = {
        "ruta_por_defecto": "E:\\ARCADES\\RetroBat\\ROMs\\psp",
        "extensiones_soportadas": [".chd", ".cso", ".pbp", ".iso", ".bin", ".zip", ".7z"],
        "umbral_franquicia": 80,
        "umbral_juego": 90,
        "palabras_vacias": ["the", "el", "la", "los", "las", "de", "of", "and", "y", "a"]
    }
    return configuracion