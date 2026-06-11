import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItem
from grouper.sorting import clave_ordenamiento

def poblar_arbol_logico(modelo, grupos):
    raiz = modelo.invisibleRootItem()
    raiz.removeRows(0, raiz.rowCount())
    _agregar_grupos_a_raiz(raiz, grupos)

def _agregar_grupos_a_raiz(raiz, grupos):
    franquicias_ordenadas = sorted(grupos.keys(), key=clave_ordenamiento)
    for nombre_franquicia in franquicias_ordenadas:
        juegos = grupos[nombre_franquicia]
        
        # Nivel 1: Franquicia (Logo de carpeta)
        item_franquicia = QStandardItem(f"📁 {nombre_franquicia}")
        item_franquicia.setEditable(True)
        item_franquicia.setData("franquicia", Qt.ItemDataRole.UserRole)
        
        juegos_ordenados = sorted(juegos.keys(), key=clave_ordenamiento)
        for nombre_juego in juegos_ordenados:
            rutas = juegos[nombre_juego]
            
            # Nivel 2: Juego (Mando)
            item_juego = QStandardItem(f"🎮 {nombre_juego}")
            item_juego.setEditable(True)
            item_juego.setData("juego", Qt.ItemDataRole.UserRole)
            
            rutas_ordenadas = sorted(rutas, key=lambda x: clave_ordenamiento(os.path.basename(x)))
            for ruta in rutas_ordenadas:
                # Nivel 3: Archivo (Disco)
                item_archivo = QStandardItem(f"💿 {os.path.basename(ruta)}")
                item_archivo.setEditable(False)
                item_archivo.setData(ruta, Qt.ItemDataRole.UserRole)
                item_archivo.setData("archivo", Qt.ItemDataRole.UserRole + 1)
                item_juego.appendRow(item_archivo)
                
            item_franquicia.appendRow(item_juego)
        raiz.appendRow(item_franquicia)