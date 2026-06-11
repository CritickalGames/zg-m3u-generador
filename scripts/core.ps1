Set-File "src/UI/widgets/status_bar.py" @"
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel

class BarraEstadoCompacta(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("status_bar_container")
        self._etiqueta = QLabel("✅ Listo.")
        self._configurar_layout()

    def _configurar_layout(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(2, 0, 2, 0)
        layout.setSpacing(0)
        layout.addWidget(self._etiqueta)
        self.setLayout(layout)

    def mostrar_mensaje(self, mensaje):
        self._etiqueta.setText("✅ " + mensaje)

    def mostrar_error(self, mensaje):
        self._etiqueta.setText("❌ " + mensaje)
"@

Set-File "src/UI/widgets/physical_tree.py" @"
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTreeView, QLabel
from PyQt6.QtGui import QStandardItemModel

class PanelArbolFisico(QWidget):
    def __init__(self):
        super().__init__()
        self._etiqueta = QLabel("🎮 <b>Vista Física</b>")
        self._modelo = QStandardItemModel()
        self._vista = QTreeView()
        self._vista.setModel(self._modelo)
        self._vista.setEditTriggers(QTreeView.EditTrigger.NoEditTriggers)
        self._configurar_layout()

    def _configurar_layout(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)
        layout.addWidget(self._etiqueta)
        layout.addWidget(self._vista)
        self.setLayout(layout)

    def obtener_modelo(self):
        return self._modelo

    def obtener_vista(self):
        return self._vista
"@

Set-File "src/UI/widgets/logical_tree.py" @"
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTreeView, QLineEdit, QLabel
from PyQt6.QtGui import QStandardItemModel

class PanelArbolLogico(QWidget):
    def __init__(self):
        super().__init__()
        self._etiqueta = QLabel("🧠 <b>Vista Lógica</b>")
        self._buscador = QLineEdit()
        self._buscador.setPlaceholderText("🔍 Buscar franquicia o juego...")
        self._modelo = QStandardItemModel()
        self._vista = QTreeView()
        self._vista.setModel(self._modelo)
        self._configurar_layout()

    def _configurar_layout(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)
        layout.addWidget(self._etiqueta)
        layout.addWidget(self._buscador)
        layout.addWidget(self._vista)
        self.setLayout(layout)

    def obtener_modelo(self):
        return self._modelo

    def obtener_vista(self):
        return self._vista

    def conectar_busqueda(self, funcion):
        self._buscador.textChanged.connect(funcion)
"@

Set-File "src/UI/widgets/top_bar.py" @"
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
        layout.setSpacing(2)
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
"@

Set-File "src/UI/app.py" @"
from PyQt6.QtWidgets import QMainWindow, QSplitter, QMessageBox, QApplication
from PyQt6.QtCore import Qt
from UI.widgets.top_bar import BarraSuperior
from UI.widgets.logical_tree import PanelArbolLogico
from UI.widgets.physical_tree import PanelArbolFisico
from UI.widgets.status_bar import BarraEstadoCompacta
from UI.logic.actions.clipboard import PortapapelesInterno
from UI.logic.actions.tree_editor import EditorArbol
from UI.logic.actions.shortcuts import configurar_atajos
from UI.logic.builders.logical import poblar_arbol_logico
from UI.logic.builders.physical import poblar_arbol_fisico
from UI.logic.filters.fuzzy_filter import FiltroFuzzyProxyModel
from UI.exporter.m3u import generar_archivos_m3u
from core.config_loader import cargar_configuracion
from scanner.fs import escanear_roms, obtener_arbol_directorios
from grouper.fuzzy import agrupar_roms_fuzzy
import os

class ROMOrganizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self._ruta_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._config = cargar_configuracion(self._ruta_base)
        self._inicializar_componentes()
        self._configurar_ventana()
        self._conectar_senales()

    def _inicializar_componentes(self):
        self._barra_superior = BarraSuperior()
        self._panel_logico = PanelArbolLogico()
        self._panel_fisico = PanelArbolFisico()
        self._barra_estado = BarraEstadoCompacta()
        self._portapapeles = PortapapelesInterno()
        self._editor = EditorArbol(self._panel_logico.obtener_vista(), self._portapapeles)
        self._filtro = FiltroFuzzyProxyModel(
            self._panel_logico.obtener_vista(),
            self._panel_logico.obtener_modelo()
        )

    def _configurar_ventana(self):
        self.setWindowTitle("🎮 ROM Organizer & M3U Generator")
        self.resize(1200, 700)
        contenedor = self._construir_layout_principal()
        self.setCentralWidget(contenedor)

    def _construir_layout_principal(self):
        from PyQt6.QtWidgets import QWidget, QVBoxLayout
        contenedor = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)
        layout.addWidget(self._barra_superior)
        divisor = QSplitter(Qt.Orientation.Horizontal)
        divisor.addWidget(self._panel_fisico)
        divisor.addWidget(self._panel_logico)
        divisor.setSizes([480, 720])
        divisor.setHandleWidth(1)
        layout.addWidget(divisor)
        layout.addWidget(self._barra_estado)
        contenedor.setLayout(layout)
        return contenedor

    def _conectar_senales(self):
        self._barra_superior.conectar_buscar(self._seleccionar_carpeta)
        self._barra_superior.conectar_escanear(self._ejecutar_escaneo)
        self._barra_superior.conectar_generar(self._ejecutar_generacion)
        self._panel_logico.conectar_busqueda(self._filtro.aplicar_filtro)
        configurar_atajos(self, self._editor)

    def _seleccionar_carpeta(self):
        from PyQt6.QtWidgets import QFileDialog
        ruta = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de ROMs")
        if ruta:
            self._barra_superior.establecer_ruta(ruta)
            self._barra_superior.activar_botones()
            self._barra_estado.mostrar_mensaje(f"Carpeta seleccionada: {ruta}")

    def _ejecutar_escaneo(self):
        ruta = self._barra_superior.obtener_ruta()
        if not ruta:
            return
        try:
            archivos = escanear_roms(ruta, self._config["extensiones_soportadas"])
            arbol = obtener_arbol_directorios(ruta)
            grupos = agrupar_roms_fuzzy(archivos, self._config)
            poblar_arbol_fisico(self._panel_fisico.obtener_modelo(), arbol)
            poblar_arbol_logico(self._panel_logico.obtener_modelo(), grupos)
            self._grupos_actuales = grupos
            self._barra_estado.mostrar_mensaje(f"✅ {len(archivos)} ROMs en {ruta}")
        except Exception as e:
            self._barra_estado.mostrar_error(str(e))

    def _ejecutar_generacion(self):
        if not hasattr(self, "_grupos_actuales"):
            return
        from PyQt6.QtWidgets import QFileDialog
        destino = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de destino")
        if destino:
            rutas = generar_archivos_m3u(self._grupos_actuales, destino)
            self._barra_estado.mostrar_mensaje(f"💾 {len(rutas)} archivos M3U generados")
"@

Set-File "main.py" @"
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from UI.app import ROMOrganizerApp

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # QSS para compacidad extrema (elimina aire interno de Qt)
    app.setStyleSheet("""
        QWidget { margin: 0px; }
        QLineEdit { padding: 2px 4px; margin: 0px; }
        QPushButton { padding: 2px 6px; margin: 0px; }
        QTreeView { padding: 0px; margin: 0px; border: 1px solid #a0a0a0; }
        QTreeView::item { padding: 1px 2px; margin: 0px; }
        QLabel { padding: 0px; margin: 0px; }
        QSplitter::handle { background-color: #a0a0a0; width: 1px; margin: 0px; }
    """)

    # Fuente ligeramente más compacta
    font = QFont("Segoe UI", 9)
    app.setFont(font)

    window = ROMOrganizerApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
"@