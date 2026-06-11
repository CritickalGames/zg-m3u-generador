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
from UI.logic.filters.fuzzy_filter import FiltroFuzzyProxyModel
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
        
        self._filtro = FiltroFuzzyProxyModel(
            self._panel_logico.obtener_vista(), 
            self._panel_logico.obtener_modelo()
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
        self._panel_logico.conectar_busqueda(self._filtro.aplicar_filtro)

    def _precargar_ruta(self):
        ruta = self._config.get("ruta_por_defecto", "")
        if ruta and os.path.exists(ruta):
            self._barra_superior.establecer_ruta(ruta)
            self._barra_superior.activar_botones()
            self._barra_estado.mostrar_mensaje(f"Ruta cargada: {ruta}")
        elif ruta:
            self._barra_superior.establecer_ruta(ruta)

    def _seleccionar_carpeta(self):
        # Se pasa la ruta por defecto como directorio inicial del diálogo
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
            poblar_arbol_logico(self._panel_logico.obtener_modelo(), grupos)
            
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
                self._panel_logico.obtener_modelo(),
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