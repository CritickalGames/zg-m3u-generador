from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton

class BarraSuperior(QWidget):
    def __init__(self):
        super().__init__()
        self._entrada_ruta = QLineEdit()
        self._btn_buscar = QPushButton("📂 Buscar")
        self._btn_escanear = QPushButton("🔍 Escanear")
        self._btn_generar = QPushButton("💾 Generar")
        self._configurar_layout()
        self._desactivar_botones_accion()

    def _configurar_layout(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._entrada_ruta)
        layout.addWidget(self._btn_buscar)
        layout.addWidget(self._btn_escanear)
        layout.addWidget(self._btn_generar)
        self.setLayout(layout)

    def _desactivar_botones_accion(self):
        self._btn_escanear.setEnabled(False)
        self._btn_generar.setEnabled(False)

    def obtener_ruta(self):
        return self._entrada_ruta.text()

    def establecer_ruta(self, ruta):
        self._entrada_ruta.setText(ruta)

    def conectar_buscar(self, funcion):
        self._btn_buscar.clicked.connect(funcion)

    def conectar_escanear(self, funcion):
        self._btn_escanear.clicked.connect(funcion)

    def conectar_generar(self, funcion):
        self._btn_generar.clicked.connect(funcion)

    def activar_botones(self):
        self._btn_escanear.setEnabled(True)
        self._btn_generar.setEnabled(True)