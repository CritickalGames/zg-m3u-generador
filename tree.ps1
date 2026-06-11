#- 1. Forzar codificación UTF-8
$OutputEncoding = [console]::InputEncoding = [console]::OutputEncoding = New-Object System.Text.UTF8Encoding

#- 2. Función de creación (UTF-8 sin BOM)
function Set-File {
    param([string]$Path, [string]$Content)
    $fullPath = Join-Path $PSScriptRoot $Path
    $dir = Split-Path $fullPath -Parent
    if (!(Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($fullPath, $Content, $utf8NoBom)
    Write-Host "  [OK] $Path" -ForegroundColor Green
}

Write-Host "🚀 Iniciando construcción del proyecto..." -ForegroundColor Cyan
Write-Host "----------------------------------------------------" -ForegroundColor DarkGray

# ==============================================================================
# SRC/UI/LOGIC/FILTERS/FUZZY_FILTER.PY (Proxy Model real y funcional)
# ==============================================================================
Set-File "src/UI/logic/filters/fuzzy_filter.py" @'
from PyQt6.QtCore import QSortFilterProxyModel, Qt, QModelIndex
from rapidfuzz import fuzz

class FiltroFuzzyProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._umbral = 60
        self._texto_busqueda = ""

    def set_texto_busqueda(self, texto: str):
        self._texto_busqueda = texto.lower().strip()
        self.invalidateFilter() # Fuerza a reevaluar todo el árbol

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        # Si no hay búsqueda, mostrar todo
        if not self._texto_busqueda:
            return True
        
        modelo_origen = self.sourceModel()
        indice = modelo_origen.index(source_row, 0, source_parent)
        
        # 1. Comprobar si el elemento actual coincide
        texto_item = str(modelo_origen.data(indice, Qt.ItemDataRole.DisplayRole)).lower()
        if fuzz.partial_ratio(self._texto_busqueda, texto_item) >= self._umbral:
            return True
        
        # 2. Comprobar si algún hijo coincide (para mantener visible a los padres)
        if modelo_origen.hasChildren(indice):
            for i in range(modelo_origen.rowCount(indice)):
                if self.filterAcceptsRow(i, indice):
                    return True
        
        return False
'@

# ==============================================================================
# SRC/UI/WIDGETS/LOGICAL_TREE.PY (Integración del Proxy Model)
# ==============================================================================
Set-File "src/UI/widgets/logical_tree.py" @'
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
'@

# ==============================================================================
# SRC/APP.PY (Conexión corregida al nuevo método filtrar)
# ==============================================================================
Set-File "src/app.py" @'
import os
from PyQt6.QtWidgets import (
    QMainWindow, QSplitter, QFileDialog, QMessageBox, 
    QApplication, QWidget, QVBoxLayout, QSizePolicy
)
from PyQt6.QtCore import Qt
from UI.widgets.top_bar import BarraSuperior
from UI.widgets.logical_tree import PanelArbolLogico
from UI.widgets.physical_tree import PanelArbolFisico
from UI.widgets.status_bar import BarraEstadoCompacta
from UI.logic.builders.logical import poblar_arbol_logico
from UI.logic.builders.physical import poblar_arbol_fisico
from UI.exporter.m3u import generar_archivos_m3u
from core.config_loader import cargar_configuracion, actualizar_ruta_por_defecto
from scanner.fs import escanear_roms, obtener_arbol_directorios
from grouper.fuzzy import agrupar_roms_fuzzy

class ROMOrganizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self._ruta_base = os.path.dirname(os.path.abspath(__file__))
        self._config = cargar_configuracion(self._ruta_base)
        self._inicializar_componentes()
        self._configurar_ventana()
        self._conectar_senales()
        self._precargar_ruta()

    def _inicializar_componentes(self):
        self._barra_superior = BarraSuperior()
        self._panel_fisico = PanelArbolFisico()
        self._panel_logico = PanelArbolLogico()
        self._barra_estado = BarraEstadoCompacta()

    def _configurar_ventana(self):
        self.setWindowTitle("🎮 ROM Organizer & M3U Generator")
        self.resize(800, 600)
        contenedor = self._construir_layout_principal()
        self.setCentralWidget(contenedor)

    def _construir_layout_principal(self):
        contenedor = QWidget()
        layout = QVBoxLayout(contenedor)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        layout.addWidget(self._barra_superior)
        
        divisor = QSplitter(Qt.Orientation.Horizontal)
        divisor.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        divisor.addWidget(self._panel_fisico)
        divisor.addWidget(self._panel_logico)
        divisor.setSizes([320, 480])
        divisor.setHandleWidth(1)
        
        layout.addWidget(divisor)
        layout.addWidget(self._barra_estado)
        return contenedor

    def _conectar_senales(self):
        self._barra_superior.conectar_buscar(self._seleccionar_carpeta)
        self._barra_superior.conectar_escanear(self._ejecutar_escaneo)
        self._barra_superior.conectar_generar(self._ejecutar_generacion)
        # Conexión directa al método filtrar del panel
        self._panel_logico._buscador.textChanged.connect(self._panel_logico.filtrar)

    def _precargar_ruta(self):
        ruta = self._config.get("ruta_por_defecto", "")
        if ruta and os.path.exists(ruta):
            self._barra_superior.establecer_ruta(ruta)
            self._barra_superior.activar_botones()
            self._barra_estado.mostrar_mensaje(f"Ruta cargada: {ruta}")
        elif ruta:
            self._barra_superior.establecer_ruta(ruta)

    def _seleccionar_carpeta(self):
        ruta_inicial = self._config.get("ruta_por_defecto", "")
        ruta = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de ROMs", ruta_inicial)
        if ruta:
            self._barra_superior.establecer_ruta(ruta)
            self._barra_superior.activar_botones()
            self._guardar_nueva_ruta(ruta)
            self._barra_estado.mostrar_mensaje(f"Carpeta seleccionada: {ruta}")

    def _guardar_nueva_ruta(self, ruta):
        actualizar_ruta_por_defecto(self._ruta_base, self._config, ruta)

    def _ejecutar_escaneo(self):
        ruta = self._barra_superior.obtener_ruta()
        if not ruta:
            return
        try:
            self._barra_estado.mostrar_mensaje("Escaneando y agrupando...")
            QApplication.processEvents()
            extensiones = set(self._config["extensiones_soportadas"])
            archivos = escanear_roms(ruta, extensiones, self._config.get("escaneo_recursivo", True))
            if not archivos:
                QMessageBox.warning(self, "Sin resultados", "No se encontraron ROMs con las extensiones configuradas.")
                self._barra_estado.mostrar_mensaje("Listo.")
                return
            
            arbol = obtener_arbol_directorios(ruta)
            grupos = agrupar_roms_fuzzy(archivos, self._config["umbral_fuzzy"])
            
            poblar_arbol_fisico(self._panel_fisico.obtener_modelo(), arbol)
            # Poblar el modelo fuente, no el de la vista
            poblar_arbol_logico(self._panel_logico.obtener_modelo_fuente(), grupos)
            
            self._panel_logico.expandir_todo()
            self._barra_estado.mostrar_mensaje(f"Listo. {len(archivos)} ROMs agrupadas.")
        except Exception as e:
            self._barra_estado.mostrar_error(str(e))

    def _ejecutar_generacion(self):
        ruta_base = self._barra_superior.obtener_ruta()
        destino = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de destino", ruta_base)
        if not destino:
            return
        try:
            fran, games, dir_salida = generar_archivos_m3u(
                self._panel_logico.obtener_modelo_fuente(), # Exportar desde el modelo fuente completo
                ruta_base,
                destino,
                self._config.get("m3u_solo_multidisco", False)
            )
            QMessageBox.information(
                self, "Éxito",
                f"Generación completada.\n\n"
                f"📁 Franquicias (.m3u): {fran}\n"
                f"🎮 Juegos (.m3u): {games}\n\n"
                f"Guardados en: {dir_salida}"
            )
            self._barra_estado.mostrar_mensaje(f"💾 {fran + games} archivos M3U generados")
        except Exception as e:
            self._barra_estado.mostrar_error(str(e))
'@