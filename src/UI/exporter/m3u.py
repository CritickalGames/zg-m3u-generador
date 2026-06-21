import os
import re
from pathlib import Path
from PyQt6.QtCore import Qt

def generar_archivos_m3u(modelo_arbol, ruta_base, ruta_salida, m3u_solo=False):
    output_dir = Path(ruta_salida)
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
        
    base_dir = Path(ruta_base)
    root = modelo_arbol.invisibleRootItem()
    
    franchises_created = 0
    games_created = 0
    
    for row in range(root.rowCount()):
        fran_item = root.child(row)
        franchise_name = fran_item.text().replace("🎮 ", "").strip()
        safe_fran_name = re.sub(r'[<>:"/\\|?*]', '_', franchise_name)
        fran_m3u_paths = []
        
        for g_row in range(fran_item.rowCount()):
            game_item = fran_item.child(g_row)
            game_name = game_item.text().replace("🎮 ", "").strip()
            safe_game_name = re.sub(r'[<>:"/\\|?*]', '_', game_name)
            game_m3u_paths = []
            
            for f_row in range(game_item.rowCount()):
                file_item = game_item.child(f_row)
                # Ahora Qt está correctamente importado
                abs_path = Path(file_item.data(Qt.ItemDataRole.UserRole))
                
                try:
                    rel_path = abs_path.relative_to(base_dir).as_posix()
                except ValueError:
                    rel_path = abs_path.as_posix()
                    
                game_m3u_paths.append(rel_path)
                fran_m3u_paths.append(rel_path)
                
            if len(game_m3u_paths) > 1 or m3u_solo:
                m3u_file = output_dir / f"{safe_game_name}.m3u"
                with open(m3u_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(game_m3u_paths))
                games_created += 1
                
        if len(fran_m3u_paths) > 1 or m3u_solo:
            m3u_file = output_dir / f"_{safe_fran_name}.m3u"
            with open(m3u_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(fran_m3u_paths))
            franchises_created += 1
            
    return franchises_created, games_created, str(output_dir)