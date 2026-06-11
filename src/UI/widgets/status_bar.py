from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel

class BarraEstadoCompacta(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("status_bar_container")
        self._etiqueta = QLabel("✅ Listo.")
        self._configurar_layout()

    def _configurar_layout(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._etiqueta)
        self.setLayout(layout)

    def mostrar_mensaje(self, mensaje):
        self._etiqueta.setText("✅ " + mensaje)

    def mostrar_error(self, mensaje):
        self._etiqueta.setText("❌ " + mensaje)