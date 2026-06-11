from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTreeView, QLineEdit, QHeaderView, QAbstractItemView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel
from UI.logic.filters.fuzzy_filter import FiltroFuzzyProxyModel

class PanelArbolLogico(QWidget):
    def __init__(self):
        super().__init__()
        self._buscador = QLineEdit()
        self._buscador.setPlaceholderText("🔍 Buscar franquicia o juego...")
        
        # Modelo fuente (contiene todos los datos)
        self._modelo_fuente = QStandardItemModel()
        self._modelo_fuente.setHorizontalHeaderLabels(["🔍 Vista Lógica (Estructura agrupada)"])
        
        # Modelo proxy (filtra lo que ve el usuario)
        self._filtro = FiltroFuzzyProxyModel()
        self._filtro.setSourceModel(self._modelo_fuente)
        
        # La vista se conecta al proxy, no al modelo fuente
        self._vista = QTreeView()
        self._vista.setModel(self._filtro)
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

    def obtener_modelo_fuente(self):
        return self._modelo_fuente

    def obtener_vista(self):
        return self._vista

    def filtrar(self, texto: str):
        self._filtro.set_texto_busqueda(texto)

    def expandir_todo(self):
        # Expandimos la vista (que muestra el proxy)
        self._vista.expandAll()