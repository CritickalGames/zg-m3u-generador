# ==============================================================================
# * WIDGET: Panel de Árbol Lógico (Editable + Búsqueda Fuzzy)
# ==============================================================================
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTreeView, QHeaderView,
    QAbstractItemView, QLineEdit
)
from PyQt6.QtGui import QStandardItemModel
from PyQt6.QtCore import Qt
from deprecated.ui.logic.filters import FuzzyFilterProxyModel


class LogicalTreePanel(QWidget):
    """
    Panel derecho con árbol lógico + barra de búsqueda fuzzy.

    ^ Responsabilidad:
        - Mostrar la estructura lógica (franquicias -> juegos -> versiones).
        - Permitir edición, drag & drop, selección múltiple.
        - Filtrar en tiempo real según búsqueda fuzzy.

    ? Nota:
        Expone dos modelos:
        - self.model: el modelo fuente (el "real")
        - self.proxy: el proxy filtrado (el que ve el tree view)
    """

    def __init__(self, model: QStandardItemModel, parent=None):
        super().__init__(parent)
        self.model = model
        self.proxy = FuzzyFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Etiqueta descriptiva
        layout.addWidget(QLabel("🧠 <b>Vista Lógica</b> (Agrupada por similitud)"))

        # ------------------------------------------------------------------
        # * 🔍 Barra de búsqueda fuzzy
        # ------------------------------------------------------------------
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Buscar franquicia o juego...")
        self.search_input.setClearButtonEnabled(True)
        # Conectar cambios de texto al filtro del proxy
        self.search_input.textChanged.connect(self.proxy.set_filter_text)
        layout.addWidget(self.search_input)

        # ------------------------------------------------------------------
        # * 🌳 TreeView editable (usa el proxy, no el modelo directo)
        # ------------------------------------------------------------------
        self.tree = QTreeView()
        self.tree.setModel(self.proxy)  # ! Importante: proxy, no model

        # ✏️ Edición: doble clic o F2
        self.tree.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked |
            QAbstractItemView.EditTrigger.EditKeyPressed
        )

        # 🖱️ Drag & drop interno
        self.tree.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.tree.setDefaultDropAction(Qt.DropAction.MoveAction)

        # 🔀 Selección múltiple
        self.tree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        # 📏 Columna única expansible
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        # 🎬 Animación
        self.tree.setAnimated(True)

        # ! Expandir automáticamente cuando el filtro muestra resultados
        self.proxy.rowsInserted.connect(self._auto_expand_on_filter)
        self.proxy.rowsRemoved.connect(self._auto_expand_on_filter)

        layout.addWidget(self.tree)

    def expand_all(self):
        """Expande todos los nodos del árbol."""
        self.tree.expandAll()

    def _auto_expand_on_filter(self):
        """
        Expande el árbol automáticamente cuando cambia el filtro.

        ¿Por qué existe?
            Cuando el usuario busca "FF7", queremos que la franquicia
            "Final Fantasy" aparezca expandida mostrando el juego coincidente
            sin tener que hacer clic en ella.
        """
        if self.search_input.text().strip():
            self.tree.expandAll()