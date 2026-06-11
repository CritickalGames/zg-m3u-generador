import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItem
from grouper.sorting import clave_ordenamiento

def poblar_arbol_fisico(modelo, arbol):
    raiz = modelo.invisibleRootItem()
    raiz.removeRows(0, raiz.rowCount())
    _agregar_nodo(raiz, arbol)

def _agregar_nodo(padre, nodo):
    item = _crear_item_carpeta(nodo)
    _agregar_archivos(item, nodo.get("archivos", []))
    _agregar_subcarpetas(item, nodo.get("hijos", []))
    padre.appendRow(item)

def _crear_item_carpeta(nodo):
    # Carpetas físicas con logo de carpeta
    item = QStandardItem(f"📁 {nodo['nombre']}")
    item.setEditable(False)
    item.setData(nodo["ruta"], Qt.ItemDataRole.UserRole)
    item.setData("carpeta", Qt.ItemDataRole.UserRole + 1)
    return item

def _agregar_archivos(item_padre, archivos):
    archivos_ordenados = sorted(archivos, key=lambda x: clave_ordenamiento(os.path.basename(x)))
    for ruta in archivos_ordenados:
        item_archivo = _crear_item_archivo(ruta)
        item_padre.appendRow(item_archivo)

def _crear_item_archivo(ruta):
    nombre = os.path.basename(ruta)
    # Archivos ROM con logo de disco
    item = QStandardItem(f"💿 {nombre}")
    item.setEditable(False)
    item.setData(ruta, Qt.ItemDataRole.UserRole)
    item.setData("archivo", Qt.ItemDataRole.UserRole + 1)
    return item

def _agregar_subcarpetas(item_padre, hijos):
    hijos_ordenados = sorted(hijos, key=lambda x: clave_ordenamiento(x["nombre"]))
    for hijo in hijos_ordenados:
        _agregar_nodo(item_padre, hijo)