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
# SRC/UI/LOGIC/ACTIONS/SHORTCUTS.PY
# ==============================================================================
Set-File "src/UI/logic/actions/shortcuts.py" @'
from PyQt6.QtGui import QKeySequence, QShortcut

def configurar_atajos(ventana, editor):
    _registrar_atajo(ventana, QKeySequence("Ctrl+Z"), editor.deshacer)
    _registrar_atajo(ventana, QKeySequence("Ctrl+Y"), editor.rehacer)
    _registrar_atajo(ventana, QKeySequence("Ctrl+X"), editor.cortar)
    _registrar_atajo(ventana, QKeySequence("Ctrl+C"), editor.copiar)
    _registrar_atajo(ventana, QKeySequence("Ctrl+V"), editor.pegar)
    _registrar_atajo(ventana, QKeySequence("Delete"), editor.eliminar)
    _registrar_atajo(ventana, QKeySequence("F2"), editor.renombrar)

def _registrar_atajo(ventana, secuencia, accion):
    atajo = QShortcut(secuencia, ventana)
    atajo.activated.connect(accion)
'@

# ==============================================================================
# SRC/UI/LOGIC/ACTIONS/TREE_EDITOR.PY (Adaptado para QSortFilterProxyModel)
# ==============================================================================
Set-File "src/UI/logic/actions/tree_editor.py" @'
from PyQt6.QtGui import QUndoStack, QStandardItem
from PyQt6.QtCore import Qt
from UI.logic.actions.clipboard import PortapapelesInterno
from UI.logic.actions.commands.rename import ComandoRenombrar
from UI.logic.actions.commands.remove import ComandoEliminar
from UI.logic.actions.commands.cut import ComandoCortar
from UI.logic.actions.commands.paste import ComandoPegar

class EditorArbol:
    def __init__(self, vista, modelo_fuente, portapapeles):
        self._vista = vista
        self._modelo_fuente = modelo_fuente
        self._portapapeles = portapapeles
        self._pila = QUndoStack()

    def deshacer(self):
        if self._pila.canUndo():
            self._pila.undo()

    def rehacer(self):
        if self._pila.canRedo():
            self._pila.redo()

    def cortar(self):
        nodos = self._obtener_nodos_fuente_seleccionados()
        if nodos:
            self._portapapeles.guardar_corte(nodos)
            self._pila.push(ComandoCortar(self._modelo_fuente, nodos))

    def copiar(self):
        nodos = self._obtener_nodos_fuente_seleccionados()
        if nodos:
            self._portapapeles.guardar_copia(nodos)

    def pegar(self):
        if self._portapapeles.esta_vacio():
            return
        destino = self._obtener_destino_fuente()
        if destino:
            self._pila.push(ComandoPegar(destino, self._portapapeles.obtener_nodos(), self._portapapeles.obtener_modo()))

    def eliminar(self):
        nodos = self._obtener_nodos_fuente_seleccionados()
        if nodos:
            self._pila.push(ComandoEliminar(self._modelo_fuente, nodos))

    def renombrar(self):
        indices = self._vista.selectedIndexes()
        if indices:
            # Mapear al modelo fuente para editar
            proxy_index = indices[0]
            if proxy_index.column() == 0:
                source_index = self._vista.model().mapToSource(proxy_index)
                self._vista.edit(source_index)

    def _obtener_nodos_fuente_seleccionados(self):
        indices = self._vista.selectedIndexes()
        proxy_model = self._vista.model()
        nodos = []
        for i in indices:
            if i.column() == 0:
                source_index = proxy_model.mapToSource(i)
                item = self._modelo_fuente.itemFromIndex(source_index)
                if item and item not in nodos:
                    nodos.append(item)
        return nodos

    def _obtener_destino_fuente(self):
        indices = self._vista.selectedIndexes()
        if not indices:
            return self._modelo_fuente.invisibleRootItem()
        
        proxy_model = self._vista.model()
        source_index = proxy_model.mapToSource(indices[0])
        item = self._modelo_fuente.itemFromIndex(source_index)
        return item if item else self._modelo_fuente.invisibleRootItem()
'@

# ==============================================================================
# SRC/UI/LOGIC/ACTIONS/CLIPBOARD.PY
# ==============================================================================
Set-File "src/UI/logic/actions/clipboard.py" @'
class PortapapelesInterno:
    def __init__(self):
        self._nodos = []
        self._modo = None

    def guardar_corte(self, nodos):
        self._nodos = nodos
        self._modo = "corte"

    def guardar_copia(self, nodos):
        self._nodos = nodos
        self._modo = "copia"

    def obtener_nodos(self):
        return self._nodos

    def obtener_modo(self):
        return self._modo

    def esta_vacio(self):
        return len(self._nodos) == 0

    def limpiar(self):
        self._nodos = []
        self._modo = None
'@

# ==============================================================================
# SRC/UI/LOGIC/ACTIONS/COMMANDS/RENAME.PY
# ==============================================================================
Set-File "src/UI/logic/actions/commands/rename.py" @'
from PyQt6.QtGui import QUndoCommand

class ComandoRenombrar(QUndoCommand):
    def __init__(self, nodo, nombre_nuevo):
        super().__init__("Renombrar")
        self._nodo = nodo
        self._nombre_nuevo = nombre_nuevo
        self._nombre_anterior = nodo.text()

    def redo(self):
        self._nodo.setText(self._nombre_nuevo)

    def undo(self):
        self._nodo.setText(self._nombre_anterior)
'@

# ==============================================================================
# SRC/UI/LOGIC/ACTIONS/COMMANDS/REMOVE.PY
# ==============================================================================
Set-File "src/UI/logic/actions/commands/remove.py" @'
from PyQt6.QtGui import QUndoCommand

class ComandoEliminar(QUndoCommand):
    def __init__(self, modelo, nodos):
        super().__init__("Eliminar")
        self._modelo = modelo
        self._nodos = nodos
        self._padres = [(n.parent() or modelo.invisibleRootItem(), n.row()) for n in nodos]

    def redo(self):
        for padre, fila in reversed(self._padres):
            padre.takeRow(fila)

    def undo(self):
        for (padre, fila), nodo in zip(self._padres, self._nodos):
            padre.insertRow(fila, nodo)
'@

# ==============================================================================
# SRC/UI/LOGIC/ACTIONS/COMMANDS/CUT.PY
# ==============================================================================
Set-File "src/UI/logic/actions/commands/cut.py" @'
from PyQt6.QtGui import QUndoCommand

class ComandoCortar(QUndoCommand):
    def __init__(self, modelo, nodos):
        super().__init__("Cortar")
        self._modelo = modelo
        self._nodos = nodos
        self._padres = [(n.parent() or modelo.invisibleRootItem(), n.row()) for n in nodos]

    def redo(self):
        for padre, fila in reversed(self._padres):
            padre.takeRow(fila)

    def undo(self):
        for (padre, fila), nodo in zip(self._padres, self._nodos):
            padre.insertRow(fila, nodo)
'@

# ==============================================================================
# SRC/UI/LOGIC/ACTIONS/COMMANDS/PASTE.PY
# ==============================================================================
Set-File "src/UI/logic/actions/commands/paste.py" @'
from PyQt6.QtGui import QUndoCommand, QStandardItem
from PyQt6.QtCore import Qt

class ComandoPegar(QUndoCommand):
    def __init__(self, destino, nodos, modo):
        super().__init__("Pegar")
        self._destino = destino
        self._modo = modo
        self._copias = [_clonar_nodo(n) for n in nodos]
        self._filas_insertadas = []

    def redo(self):
        self._filas_insertadas = []
        for copia in self._copias:
            fila = self._destino.rowCount()
            self._destino.appendRow(copia)
            self._filas_insertadas.append(fila)

    def undo(self):
        for fila in reversed(self._filas_insertadas):
            self._destino.removeRow(fila)

def _clonar_nodo(nodo):
    copia = QStandardItem(nodo.text())
    copia.setEditable(nodo.isEditable())
    # Copiar roles de datos personalizados
    for rol in [Qt.ItemDataRole.UserRole, Qt.ItemDataRole.UserRole + 1]:
        dato = nodo.data(rol)
        if dato is not None:
            copia.setData(dato, rol)
    
    for i in range(nodo.rowCount()):
        copia.appendRow(_clonar_nodo(nodo.child(i)))
    return copia
'@

# ==============================================================================
# SRC/APP.PY (Integración del Editor y Atajos)
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
from UI.logic.actions.clipboard import PortapapelesInterno
from UI.logic.actions.tree_editor import EditorArbol
from UI.logic.actions.shortcuts import configurar_atajos
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
        
        self._portapapeles = PortapapelesInterno()
        self._editor = EditorArbol(
            self._panel_logico.obtener_vista(),
            self._panel_logico.obtener_modelo_fuente(),
            self._portapapeles
        )

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
        self._panel_logico._buscador.textChanged.connect(self._panel_logico.filtrar)
        
        # Activar atajos
        configurar_atajos(self, self._editor)

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
                self._panel_logico.obtener_modelo_fuente(),
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