
# --------------------------------------------------------------------------
# * Módulos propios del proyecto (Arquitectura por Dominios)
# --------------------------------------------------------------------------
from scanner.fs import scan_roms, get_directory_tree   # ? Escaneo del disco + estructura física
from grouper.fuzzy import group_roms_fuzzy             # ? Agrupación inteligente por similitud
from deprecated.ui.logic.tree import populate_tree                      # ? Constructor del árbol lógico
from deprecated.ui.logic.file_explorer import populate_physical_tree    # ? Constructor del árbol físico
from deprecated.ui.logic.exporter import generate_m3u_files             # ? Generador de archivos .m3u
from config import CONFIG                              # ? Configuración central

# --------------------------------------------------------------------------
# * UI Refactorizada: Widgets, Acciones y Estado
# --------------------------------------------------------------------------
from deprecated.ui.widgets import TopBar, LogicalTreePanel, PhysicalTreePanel
from deprecated.ui.actions import setup_edit_shortcuts
from deprecated.ui.actions.commands import RenameNodeCommand      # ! Comando para interceptar renombres
from deprecated.ui.logic.status_bar import CompactStatusBar


# ==============================================================================
# * CLASE PRINCIPAL: ROMOrganizerApp
# ==============================================================================
class ROMOrganizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ROM Organizer & M3U Generator")
        self.resize(800, 600)

        # ------------------------------------------------------------------
        # * Modelos de datos y Stack de Undo/Redo
        # ------------------------------------------------------------------
        self.model = QStandardItemModel()           # ? Árbol lógico (agrupado por fuzzy)
        self.physical_model = QStandardItemModel()  # ? Árbol físico (estructura real)
        self.rom_data = {}                          # - Respaldo en memoria de datos agrupados

        # ! QUndoStack reemplaza a setUndoRedoEnabled (no disponible en PyQt6)
        # - Todos los comandos de edición (borrar, renombrar, mover) se pushean aquí.
        self.undo_stack = QUndoStack(self)

        # - Conectar itemChanged para capturar renombres automáticamente
        self.model.itemChanged.connect(self._on_item_changed)

        # - Construcción de UI delegada a widgets autocontenidos.
        self._setup_ui()

    # ======================================================================
    # * ORQUESTADOR DE UI
    # ======================================================================
    def _setup_ui(self):
        """
        Ensambla los widgets refactorizados y conecta señales.
        """
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(6)

        # ------------------------------------------------------------------
        # * Widgets autocontenidos
        # ------------------------------------------------------------------
        self.top_bar = TopBar()
        self.status_bar = CompactStatusBar()

        # - Paneles del splitter: físico (izquierda) + lógico (derecha)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.physical_panel = PhysicalTreePanel(self.physical_model)
        self.logical_panel = LogicalTreePanel(self.model)

        splitter.addWidget(self.physical_panel)
        splitter.addWidget(self.logical_panel)
        splitter.setSizes([440, 660])  # ! 40% físico, 60% lógico

        # - Ensamblaje final en el layout vertical
        layout.addWidget(self.top_bar)
        layout.addWidget(splitter, stretch=1)
        layout.addWidget(self.status_bar)

        # ------------------------------------------------------------------
        # * Conexión de señales (Orquestación pura)
        # ------------------------------------------------------------------
        self.top_bar.scan_requested.connect(self.scan_and_populate)
        self.top_bar.generate_requested.connect(self.generate_m3u)

        # ------------------------------------------------------------------
        # * Atajos de edición (desacoplados)
        # ------------------------------------------------------------------
        # ! IMPORTANTE: Pasamos el proxy del árbol lógico para que las
        # operaciones de edición mapeen índices correctamente cuando
        # hay una búsqueda activa.
        setup_edit_shortcuts(
            parent=self,
            model=self.model,
            undo_stack=self.undo_stack,
            tree_view=self.logical_panel.tree,
            on_status=self.status_bar.set_message,
            proxy_model=self.logical_panel.proxy  # ! Nuevo parámetro
        )

    # ======================================================================
    # * FLUJO MACRO: Escanear y Poblar
    # ======================================================================
    def scan_and_populate(self):
        """
        Ejecuta el flujo completo de carga y agrupación de datos.
        """
        target_path = self.top_bar.get_path()

        # ------------------------------------------------------------------
        # * Validación de la ruta ingresada
        # ------------------------------------------------------------------
        if not target_path:
            QMessageBox.warning(self, "Ruta vacía", "Ingresa o selecciona una carpeta de ROMs.")
            return

        from pathlib import Path
        if not Path(target_path).exists():
            QMessageBox.warning(self, "Ruta inválida", f"La carpeta no existe:\n{target_path}")
            return

        # ------------------------------------------------------------------
        # * Limpieza de estado previo
        # ------------------------------------------------------------------
        self.model.clear()
        self.physical_model.clear()
        # ! Limpiar historial de undo/redo entre escaneos
        self.undo_stack.clear()

        self.status_bar.set_message(f"Escaneando: {target_path}...")
        QApplication.processEvents()

        # ------------------------------------------------------------------
        # * Escaneo y agrupación
        # ------------------------------------------------------------------
        roms = scan_roms(target_path)
        if not roms:
            QMessageBox.warning(
                self, "Sin resultados",
                f"No se encontraron ROMs con las extensiones configuradas en:\n{target_path}"
            )
            self.status_bar.set_message("Listo.")
            return

        # ------------------------------------------------------------------
        # * Poblado de ambos árboles
        # ------------------------------------------------------------------
        self.rom_data = group_roms_fuzzy(roms)
        populate_tree(self.model, self.rom_data)
        
        # ! Cachear textos originales para poder detectar renombres
        self._cache_model_texts(self.model.invisibleRootItem())
        self.logical_panel.expand_all()

        physical_structure = get_directory_tree(target_path)
        populate_physical_tree(self.physical_model, physical_structure)
        self.physical_panel.expand_all()

        # ------------------------------------------------------------------
        # * Actualización de estado de la UI
        # ------------------------------------------------------------------
        self.top_bar.set_generate_enabled(True)
        self.status_bar.set_message(f"Listo. {len(roms)} ROMs en {target_path}")

    # ======================================================================
    # * FLUJO MACRO: Generar Archivos .m3u
    # ======================================================================
    def generate_m3u(self):
        """
        Genera los archivos .m3u basándose en el estado actual del árbol lógico.
        """
        CONFIG["OUTPUT_DIR"] = self.top_bar.get_path()
        franchises_created, games_created, output_dir = generate_m3u_files(self.model)

        QMessageBox.information(
            self, "Éxito",
            f"Generación completada.\n\n"
            f"Franquicias (.m3u): {franchises_created}\n"
            f"Juegos (.m3u): {games_created}\n\n"
            f"Guardados en: {output_dir}"
        )

    # ======================================================================
    # * CAPTURA DE RENOMBRES (Para Undo/Redo)
    # ======================================================================
    def _cache_model_texts(self, item):
        """
        ¿Qué hace?
            Guarda el texto actual de cada item en UserRole+1.
        ¿Por qué existe?
            QStandardItemModel no guarda el "texto anterior" al emitir itemChanged.
            Al cachearlo en un rol personalizado, _on_item_changed puede comparar
            y crear el RenameNodeCommand correctamente.
        """
        item.setData(item.text(), Qt.ItemDataRole.UserRole + 1)
        for i in range(item.rowCount()):
            child = item.child(i)
            if child:
                self._cache_model_texts(child)

    def _on_item_changed(self, item):
        """
        ¿Qué hace?
            Intercepta cambios de texto en items del modelo lógico.
            Crea un RenameNodeCommand y lo pushea al QUndoStack.
        ¿Por qué existe?
            Para que los renombres hechos con F2 o doble clic sean reversibles.
        """
        old_text = item.data(Qt.ItemDataRole.UserRole + 1)
        new_text = item.text()

        if old_text is not None and old_text != new_text:
            cmd = RenameNodeCommand(item, old_text, new_text)
            self.undo_stack.push(cmd)
            # Actualizar la caché con el nuevo texto para futuros cambios
            item.setData(new_text, Qt.ItemDataRole.UserRole + 1)
        elif old_text is None:
            # Primera vez que se evalúa este item
            item.setData(new_text, Qt.ItemDataRole.UserRole + 1)