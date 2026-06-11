from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTreeView, QHeaderView, QAbstractItemView
from PyQt6.QtGui import QStandardItemModel

class PanelArbolFisico(QWidget):
    def __init__(self):
        super().__init__()
        self._modelo = QStandardItemModel()
        self._modelo.setHorizontalHeaderLabels(["📂 Vista Física (Estructura real)"])
        
        self._vista = QTreeView()
        self._vista.setModel(self._modelo)
        self._vista.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._vista.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self._vista.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._vista.setAnimated(True)
        
        self._configurar_layout()

    def _configurar_layout(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._vista)
        self.setLayout(layout)

    def obtener_modelo(self):
        return self._modelo

    def obtener_vista(self):
        return self._vista