import re
from pathlib import Path
from PyQt6.QtCore import Qt
from config import CONFIG

def generate_m3u_files(model):
    """Genera archivos .m3u por juego y por franquicia. Retorna estadísticas."""
    output_dir = Path(CONFIG["OUTPUT_DIR"])
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    base_dir = Path(CONFIG["BASE_DIR"])
    root = model.invisibleRootItem()

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
        if len(fran_m3u_paths) > 1 or CONFIG["M3U_SOLO"]:
            m3u_file = output_dir / f"_{safe_fran_name}.m3u"
            with open(m3u_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(fran_m3u_paths))
            franchises_created += 1

    return franchises_created, games_created, str(output_dir)