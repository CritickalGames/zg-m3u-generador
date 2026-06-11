# ==============================================================================
# * CLIPBOARD INTERNO: Almacén de items cortados
# ==============================================================================
# - Mantiene una referencia a los items cortados entre Ctrl+X y Ctrl+V.
# - Almacena los items con su jerarquía completa (gracias a takeRow).
#
# ^ Filosofía: El clipboard es un singleton de sesión, no persiste entre
#   ejecuciones. Si el usuario cierra la app, pierde lo cortado.
# ==============================================================================

from PyQt6.QtGui import QStandardItem
from typing import Optional


class InternalClipboard:
    """
    Portapapeles interno de la aplicación.

    ¿Qué hace?
        - Guarda los items cortados (con toda su jerarquía de hijos).
        - Provee métodos has_content() y get_items() para consultar.
        - Se limpia cuando el usuario hace un nuevo corte.

    ¿Por qué existe?
        QClipboard del sistema no soporta QStandardItem directamente.
        Necesitamos un buffer interno que preserve la estructura jerárquica
        (franquicia -> juegos -> versiones) al cortar y pegar.

    ¿Cómo se conecta con el flujo general?
        - CutCommand lo llena con items extraídos vía takeRow().
        - PasteCommand lo lee para clonar e insertar los items.
    """

    def __init__(self):
        # - Lista de tuplas: cada tupla es una fila cortada
        # - Cada fila es una lista de QStandardItem (normalmente 1 columna)
        self._items: list[list[QStandardItem]] = []

    def set_items(self, items_list: list[list[QStandardItem]]) -> None:
        """Reemplaza el contenido del clipboard con nuevos items."""
        self._items = items_list

    def get_items(self) -> list[list[QStandardItem]]:
        """Devuelve una copia de los items almacenados."""
        return self._items

    def has_content(self) -> bool:
        """Indica si hay algo disponible para pegar."""
        return len(self._items) > 0

    def clear(self) -> None:
        """Vacía el clipboard."""
        self._items = []


# Instancia global compartida entre todos los comandos de edición
clipboard = InternalClipboard()