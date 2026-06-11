from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTreeView, QLineEdit, QHeaderView, QAbstractItemView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel

class PanelArbolLogico(QWidget):
    def __init__(self):
        super().__init__()
        self._buscador = QLineEdit()
        self._buscador.setPlaceholderText("🔍 Buscar franquicia o juego...")
        
        self._modelo = QStandardItemModel()
        self._modelo.setHorizontalHeaderLabels(["🔍 Vista Lógica (Estructura agrupada)"])
        
        self._vista = QTreeView()
        self._vista.setModel(self._modelo)
        self._vista.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.EditKeyPressed)
        self._vista.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self._vista.setDefaultDropAction(Qt.DropAction.MoveAction)
        self._vista.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self._vista.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._vista.setAnimated(True)
        
        self._configurar_layout()

    def _configurar_layout(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._buscador)
        layout.addWidget(self._vista)
        self.setLayout(layout)

    def obtener_modelo(self):
        return self._modelo

    def obtener_vista(self):
        return self._vista

    def conectar_busqueda(self, funcion):
        self._buscador.textChanged.connect(funcion)

    def expandir_todo(self):
        self._vista.expandAll()