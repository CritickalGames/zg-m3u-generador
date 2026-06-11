# ==============================================================================
# * 🏷️ WIDGET: Barra de Estado Compacta
# ==============================================================================
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt


class CompactStatusBar(QLabel):
    """
    Barra de estado inferior compacta y sutil.

    ^ Responsabilidad:
        - Mostrar mensajes de estado al usuario.
        - Mantener un perfil visual discreto (altura fija, fondo sutil).

    ¿Por qué existe como clase independiente?
        Encapsula el estilo CSS y la configuración de altura en un solo
        lugar. Si mañana quieres cambiar el diseño de la barra de estado,
        solo tocas este archivo de ~30 líneas.
    """

    def __init__(self, parent=None):
        super().__init__("Listo.", parent)
        self._setup_style()

    def _setup_style(self):
        # Altura fija para no ocupar espacio vertical innecesario
        self.setFixedHeight(28)

        # Estilo sutil: fondo casi transparente, borde discreto
        self.setStyleSheet(
            "QLabel {"
            "  padding: 2px 8px;"
            "  background: rgba(255, 255, 255, 0.04);"
            "  border: 1px solid rgba(255, 255, 255, 0.08);"
            "  border-radius: 4px;"
            "  color: #a0a0b0;"
            "  font-size: 12px;"
            "}"
        )
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

    def set_message(self, text: str):
        """
        Actualiza el mensaje de estado.

        ¿Por qué un método dedicado?
            Proporciona una API semántica clara. El orquestador llama
            status_bar.set_message("...") en lugar de setText(),
            dejando espacio para añadir lógica futura (timestamps,
            colores dinámicos según tipo de mensaje, etc.).
        """
        self.setText(text)