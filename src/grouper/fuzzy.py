import os
from rapidfuzz import fuzz
from core.naming import normalizar_nombre, obtener_franquicia

def agrupar_roms_fuzzy(rom_paths: list, umbral: int) -> dict:
    groups = {}
    for rom_path in rom_paths:
        filename = os.path.basename(rom_path)
        norm_name = normalizar_nombre(filename)
        franchise = obtener_franquicia(norm_name)
        best_match_game = None
        best_score = 0
        if franchise in groups:
            for existing_game in groups[franchise].keys():
                score = fuzz.ratio(norm_name, existing_game)
                if score > best_score:
                    best_score = score
                    best_match_game = existing_game
        if best_score >= umbral and best_match_game:
            groups[franchise][best_match_game].append(rom_path)
        else:
            if franchise not in groups:
                groups[franchise] = {}
            groups[franchise][norm_name] = [rom_path]
    return groups