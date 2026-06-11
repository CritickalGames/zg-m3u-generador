# ==============================================================================
# * CONSTRUCTOR DEL ÁRBOL FÍSICO (populate_physical_tree)
# ==============================================================================
# - Construye recursivamente el árbol de directorios reales del disco.
# - Usa el mismo patrón de DecorationRole que populate_tree.
#
# ^ Filosofía: Consistencia visual entre ambos árboles usando
#   el mismo helper emoji_to_pixmap y el mismo rol DecorationRole.
# ==============================================================================

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItem
from grouper.sorting import custom_sort_key
from deprecated.ui.widgets.delegates import emoji_to_pixmap


def populate_physical_tree(model, tree_data: dict, parent_item=None):
    """
    Construye recursivamente el árbol de directorios físicos.

    ¿Qué hace?
        - Navega el diccionario anidado de carpetas/archivos.
        - Crea items con nombre limpio en DisplayRole.
        - Asigna emojis 📁 y 💿 como DecorationRole.

    ¿Por qué es recursivo?
        La estructura de carpetas puede tener profundidad arbitraria.
        La recursión natural refleja esta estructura sin límites artificiales.

    ¿Cómo se conecta con el flujo general?
        Es invocado por scan_and_populate() con el resultado de get_directory_tree().
        Sirve como mapa de referencia visual (solo lectura).
    """
    # ------------------------------------------------------------------
    # * Inicialización del nivel raíz
    # ------------------------------------------------------------------
    if parent_item is None:
        parent_item = model.invisibleRootItem()
        model.setHorizontalHeaderLabels(["Estructura de Directorios"])

    # - Separar carpetas de archivos para ordenarlos independientemente
    folders = {k: v for k, v in tree_data.items() if k != "__files__"}
    files = tree_data.get("__files__", [])

    # ------------------------------------------------------------------
    # * Carpetas: texto limpio + emoji 📁
    # ------------------------------------------------------------------
    sorted_folders = sorted(folders.keys(), key=custom_sort_key)
    for folder_name in sorted_folders:
        folder_item = QStandardItem(folder_name)  # ! Sin emoji en el texto
        folder_item.setData(emoji_to_pixmap("📁"), Qt.ItemDataRole.DecorationRole)
        folder_item.setEditable(False)
        folder_item.setToolTip(f"Carpeta: {folder_name}")
        parent_item.appendRow(folder_item)

        # - Llamada recursiva para el contenido de esta carpeta
        populate_physical_tree(model, folders[folder_name], folder_item)

    # ------------------------------------------------------------------
    # * Archivos: texto limpio + emoji 💿
    # ------------------------------------------------------------------
    sorted_files = sorted(files, key=lambda x: custom_sort_key(x.name))
    for file_path in sorted_files:
        file_item = QStandardItem(file_path.name)  # ! Sin emoji en el texto
        file_item.setData(emoji_to_pixmap("💿"), Qt.ItemDataRole.DecorationRole)
        file_item.setEditable(False)
        file_item.setData(str(file_path), Qt.ItemDataRole.UserRole)
        file_item.setToolTip(f"Ruta: {file_path}")
        parent_item.appendRow(file_item)