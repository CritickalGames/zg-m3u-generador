import os
import re

def normalizar_nombre(filename: str) -> str:
    name = os.path.splitext(filename)[0]
    name = re.sub(r'\s*[\(\[].*?[\)\]]\s*', ' ', name)
    return re.sub(r'\s+', ' ', name).strip()

def obtener_franquicia(normalized_name: str) -> str:
    parts = normalized_name.split()
    franchise_parts = []
    for part in parts:
        if any(char.isdigit() for char in part):
            break
        franchise_parts.append(part)
    if not franchise_parts:
        franchise_parts = parts[:2]
    return " ".join(franchise_parts).strip() or "Misceláneo"