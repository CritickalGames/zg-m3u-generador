# ==============================================================================
# * 📂 WIDGET: Panel de Árbol Físico (Solo Lectura)
# ==============================================================================
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTreeView, QHeaderView, QAbstractItemView
from PyQt6.QtGui import QStandardItemModel


class PhysicalTreePanel(QWidget):
    """
    Panel izquierdo con el árbol físico de directorios (solo lectura).

    ^ Responsabilidad:
        - Mostrar la estructura real de carpetas del disco.
        - Servir como mapa de referencia visual para el usuario.
        - NO permitir edición ni drag & drop.

    ? Nota:
        Al igual que LogicalTreePanel, recibe el modelo desde fuera
        para mantener la separación de responsabilidades.
    """

    def __init__(self, model: QStandardItemModel, parent=None):
        super().__init__(parent)
        self.model = model
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Etiqueta descriptiva
        layout.addWidget(QLabel("📂 <b>Vista Física</b> (Estructura real)"))

        # ------------------------------------------------------------------
        # * 🗺️ TreeView de solo lectura
        # ------------------------------------------------------------------
        self.tree = QTreeView()
        self.tree.setModel(self.model)

        # 🔒 Solo lectura
        self.tree.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tree.setDragDropMode(QAbstractItemView.DragDropMode.NoDragDrop)

        # 🔀 Selección múltiple (útil para copiar rutas)
        self.tree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        # 📏 Columna única expansible
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        # 🎬 Animación
        self.tree.setAnimated(True)

        layout.addWidget(self.tree)

    def expand_all(self):
        """Expande todos los nodos del árbol."""
        self.tree.expandAll()