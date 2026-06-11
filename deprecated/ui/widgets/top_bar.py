# ==============================================================================
# * ✏️ WIDGET: Barra Superior (TopBar)
# ==============================================================================
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton
from PyQt6.QtCore import pyqtSignal
from config import CONFIG


class TopBar(QWidget):
    """
    Barra superior autocontenida con input de ruta y botones de acción.

    ^ Responsabilidad:
        - Mostrar y editar la ruta de búsqueda de ROMs.
        - Emitir señales cuando el usuario desea escanear o generar.
        - Abrir el explorador nativo de carpetas.

    ? Señales emitidas:
        - scan_requested: El usuario pulsó "Escanear".
        - generate_requested: El usuario pulsó "Generar .m3u".
    """

    # --------------------------------------------------------------------------
    # * 📡 Señales personalizadas
    # --------------------------------------------------------------------------
    scan_requested = pyqtSignal()
    generate_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # ------------------------------------------------------------------
        # * ✏️ Input de ruta
        # ------------------------------------------------------------------
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("📁 Ruta de la carpeta de ROMs...")
        self.path_input.setText(CONFIG["BASE_DIR"])
        self.path_input.setToolTip(
            "Ruta donde se buscarán las ROMs. Edítala manualmente o usa el botón de la derecha."
        )

        # ------------------------------------------------------------------
        # * 📂 Botón: Explorador de carpetas
        # ------------------------------------------------------------------
        self.btn_browse = QPushButton("📂 Buscar carpeta")
        self.btn_browse.setToolTip("Abrir explorador de carpetas del sistema")
        self.btn_browse.clicked.connect(self._browse_folder)

        # ------------------------------------------------------------------
        # * 🔍 Botón: Escanear
        # ------------------------------------------------------------------
        self.btn_scan = QPushButton("🔍 Escanear")
        self.btn_scan.clicked.connect(self.scan_requested.emit)

        # ------------------------------------------------------------------
        # * 💾 Botón: Generar .m3u
        # ------------------------------------------------------------------
        self.btn_generate = QPushButton("💾 Generar .m3u")
        self.btn_generate.setEnabled(False)
        self.btn_generate.clicked.connect(self.generate_requested.emit)

        # ------------------------------------------------------------------
        # * 📐 Distribución
        # ------------------------------------------------------------------
        layout.addWidget(self.path_input, stretch=1)
        layout.addWidget(self.btn_browse)
        layout.addWidget(self.btn_scan)
        layout.addSpacing(12)
        layout.addWidget(self.btn_generate)

    # ----------------------------------------------------------------------
    # * 📂 Handler interno: Explorador de carpetas
    # ----------------------------------------------------------------------
    def _browse_folder(self):
        from PyQt6.QtWidgets import QFileDialog
        start_dir = self.path_input.text().strip() or CONFIG["BASE_DIR"]
        folder = QFileDialog.getExistingDirectory(
            self, "Seleccionar carpeta de ROMs", start_dir,
            QFileDialog.Option.ShowDirsOnly
        )
        if folder:
            self.path_input.setText(folder)

    # ----------------------------------------------------------------------
    # * 🔌 API pública para el orquestador
    # ----------------------------------------------------------------------
    def get_path(self) -> str:
        """Devuelve la ruta actual del input."""
        return self.path_input.text().strip()

    def set_generate_enabled(self, enabled: bool):
        """Habilita o deshabilita el botón de generar."""
        self.btn_generate.setEnabled(enabled)