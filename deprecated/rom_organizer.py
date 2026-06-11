import os
import re
import sys
from pathlib import Path
from rapidfuzz import fuzz
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QTreeView, QFileDialog, 
    QMessageBox, QHeaderView, QAbstractItemView, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QStandardItemModel, QStandardItem

# ==============================================================================
# CONFIGURACIÓN
# ==============================================================================
CONFIG = {
    "BASE_DIR": "E:/ARCADES/RetroBat/ROMs/psp",
    "RECURSIVE": True,
    "EXTENSIONS": {".chd", ".cso", ".pbp", ".iso", ".bin"},
    "FUZZY_THRESHOLD": 75,          # 0–100
    "OUTPUT_DIR": "E:/ARCADES/RetroBat/ROMs/psp",
    "M3U_SOLO": False               # False = no generar .m3u para juegos de 1 sola ROM
}

# ==============================================================================
# LÓGICA DE PROCESAMIENTO
# ==============================================================================

def normalize_name(filename: str) -> str:
    """Elimina extensión, regiones (USA) y versiones [v1.2] para comparación fuzzy."""
    name = os.path.splitext(filename)[0]
    # Elimina texto entre paréntesis o corchetes al final o en medio
    name = re.sub(r'\s*[\(\[].*?[\)\]]\s*', ' ', name)
    return re.sub(r'\s+', ' ', name).strip()

def get_franchise(normalized_name: str) -> str:
    """Heurística para extraer el nombre de la franquicia (palabras antes del primer número)."""
    parts = normalized_name.split()
    franchise_parts = []
    for part in parts:
        if any(char.isdigit() for char in part):
            break
        franchise_parts.append(part)
    
    if not franchise_parts:
        franchise_parts = parts[:2] # Fallback: primeras 2 palabras
        
    return " ".join(franchise_parts).strip() or "Misceláneo"

def custom_sort_key(name: str):
    """Orden estricto: 1. Símbolos, 2. Números, 3. Letras (insensible a mayúsculas)."""
    name = name.strip()
    if not name:
        return (3, "")
    first_char = name[0]
    if not first_char.isalnum():
        return (0, name.lower())
    elif first_char.isdigit():
        return (1, name.lower())
    else:
        return (2, name.lower())

def scan_roms():
    """Escanea el directorio y devuelve lista de rutas absolutas."""
    roms = []
    base = Path(CONFIG["BASE_DIR"])
    
    if CONFIG["RECURSIVE"]:
        for root, _, files in os.walk(base):
            for f in files:
                if Path(f).suffix.lower() in CONFIG["EXTENSIONS"]:
                    roms.append(Path(root) / f)
    else:
        for f in os.listdir(base):
            if Path(f).suffix.lower() in CONFIG["EXTENSIONS"]:
                roms.append(base / f)
                
    return roms

def group_roms_fuzzy(rom_paths: list[Path]) -> dict:
    """Agrupa ROMs usando rapidfuzz. Retorna estructura: {Franquicia: {Juego: [rutas]}}"""
    groups = {} # { "Franchise": { "Game": [Path, Path] } }
    
    for rom_path in rom_paths:
        filename = rom_path.name
        norm_name = normalize_name(filename)
        franchise = get_franchise(norm_name)
        
        best_match_game = None
        best_score = 0
        
        # Buscar si ya existe un juego similar en esta franquicia
        if franchise in groups:
            for existing_game in groups[franchise].keys():
                score = fuzz.ratio(norm_name, existing_game)
                if score > best_score:
                    best_score = score
                    best_match_game = existing_game
                    
        if best_score >= CONFIG["FUZZY_THRESHOLD"] and best_match_game:
            groups[franchise][best_match_game].append(rom_path)
        else:
            if franchise not in groups:
                groups[franchise] = {}
            groups[franchise][norm_name] = [rom_path]
            
    return groups

# ==============================================================================
# INTERFAZ GRÁFICA (PyQt6)
# ==============================================================================

class ROMOrganizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎮 ROM Organizer & M3U Generator")
        self.resize(800, 600)
        
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Nombre / Estructura"])
        
        self.setup_ui()
        self.rom_data = {} # Almacena la estructura original por si se necesita reiniciar

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Botones
        btn_layout = QHBoxLayout()
        self.btn_scan = QPushButton("🔍 Escanear Directorio")
        self.btn_scan.clicked.connect(self.scan_and_populate)
        
        self.btn_generate = QPushButton("💾 Generar archivos .m3u")
        self.btn_generate.clicked.connect(self.generate_m3u)
        self.btn_generate.setEnabled(False)
        
        btn_layout.addWidget(self.btn_scan)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_generate)
        layout.addLayout(btn_layout)
        
        # TreeView
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.EditKeyPressed)
        self.tree.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.tree.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.tree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.setAnimated(True)
        layout.addWidget(self.tree)
        
        # Info
        self.lbl_info = QLabel("Listo.")
        layout.addWidget(self.lbl_info)

    def scan_and_populate(self):
        self.model.clear()
        self.model.setHorizontalHeaderLabels(["Nombre / Estructura"])
        self.lbl_info.setText("Escaneando y agrupando...")
        QApplication.processEvents()
        
        roms = scan_roms()
        if not roms:
            QMessageBox.warning(self, "Sin resultados", "No se encontraron ROMs con las extensiones configuradas.")
            self.lbl_info.setText("Listo.")
            return
            
        self.rom_data = group_roms_fuzzy(roms)
        self.populate_tree()
        self.btn_generate.setEnabled(True)
        self.lbl_info.setText(f"Listo. {len(roms)} ROMs agrupadas.")

    def populate_tree(self):
        root = self.model.invisibleRootItem()
        
        # Ordenar franquicias
        sorted_franchises = sorted(self.rom_data.keys(), key=custom_sort_key)
        
        for franchise in sorted_franchises:
            fran_item = QStandardItem(f"📁 {franchise}")
            fran_item.setEditable(True)
            fran_item.setData("franchise", Qt.ItemDataRole.UserRole)
            
            games = self.rom_data[franchise]
            # Ordenar juegos dentro de la franquicia
            sorted_games = sorted(games.keys(), key=custom_sort_key)
            
            for game in sorted_games:
                game_item = QStandardItem(f"📂 {game}")
                game_item.setEditable(True)
                game_item.setData("game", Qt.ItemDataRole.UserRole)
                
                # Ordenar versiones/archivos dentro del juego
                sorted_files = sorted(games[game], key=lambda x: custom_sort_key(x.name))
                
                for file_path in sorted_files:
                    file_item = QStandardItem(f"🎮 {file_path.name}")
                    file_item.setEditable(False) # Los archivos no se renombran en el árbol, solo se mueven
                    file_item.setData(str(file_path), Qt.ItemDataRole.UserRole)
                    game_item.appendRow(file_item)
                    
                fran_item.appendRow(game_item)
                
            root.appendRow(fran_item)
            
        self.tree.expandAll()

    def generate_m3u(self):
        output_dir = Path(CONFIG["OUTPUT_DIR"])
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
            
        base_dir = Path(CONFIG["BASE_DIR"])
        root = self.model.invisibleRootItem()
        
        franchises_created = 0
        games_created = 0
        
        for row in range(root.rowCount()):
            fran_item = root.child(row)
            franchise_name = fran_item.text().replace("📁 ", "").strip()
            safe_fran_name = re.sub(r'[<>:"/\\|?*]', '_', franchise_name)
            
            fran_m3u_paths = []
            game_files_count = 0
            
            for g_row in range(fran_item.rowCount()):
                game_item = fran_item.child(g_row)
                game_name = game_item.text().replace("📂 ", "").strip()
                safe_game_name = re.sub(r'[<>:"/\\|?*]', '_', game_name)
                
                game_m3u_paths = []
                
                for f_row in range(game_item.rowCount()):
                    file_item = game_item.child(f_row)
                    abs_path = Path(file_item.data(Qt.ItemDataRole.UserRole))
                    
                    # Ruta relativa a BASE_DIR con slashes forward (estándar M3U)
                    rel_path = abs_path.relative_to(base_dir).as_posix()
                    
                    game_m3u_paths.append(rel_path)
                    fran_m3u_paths.append(rel_path)
                    game_files_count += 1
                    
                # Generar .m3u por JUEGO
                if game_files_count > 1 or CONFIG["M3U_SOLO"]:
                    m3u_file = output_dir / f"{safe_game_name}.m3u"
                    with open(m3u_file, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(game_m3u_paths))
                    games_created += 1
                    
            # Generar .m3u por FRANQUICIA (prefijado con _)
            # Solo si hay más de 1 archivo en total en la franquicia, o si M3U_SOLO es True
            if len(fran_m3u_paths) > 1 or CONFIG["M3U_SOLO"]:
                m3u_file = output_dir / f"_{safe_fran_name}.m3u"
                with open(m3u_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(fran_m3u_paths))
                franchises_created += 1

        QMessageBox.information(
            self, "Éxito", 
            f"Generación completada.\n\n"
            f"📁 Franquicias (.m3u): {franchises_created}\n"
            f"🎮 Juegos (.m3u): {games_created}\n\n"
            f"Guardados en: {output_dir}"
        )

# ==============================================================================
# PUNTO DE ENTRADA
# ==============================================================================
if __name__ == "__main__":
    # Configuración de estilo básico para que se vea moderno
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Fuente global
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = ROMOrganizerApp()
    window.show()
    sys.exit(app.exec())