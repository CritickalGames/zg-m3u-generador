# ==============================================================================
# * UTILIDADES DE RENDERIZADO: Conversión de emoji a QPixmap
# ==============================================================================
# - Qt soporta nativamente iconos antes del texto vía DecorationRole.
# - En lugar de un delegate personalizado (frágil), convertimos emojis
#   a QPixmap y los asignamos como decoración.
#
# ^ Ventajas sobre el delegate:
#   - Qt mantiene toda la UI nativa (selección, hover, ramas, editor inline)
#   - No hay doble pintado ni interferencia con F2
#   - Mucho menos código, menos puntos de falla
# ==============================================================================

from PyQt6.QtGui import QPixmap, QPainter, QFont
from PyQt6.QtCore import Qt


# Caché global para evitar recrear el mismo QPixmap múltiples veces
_EMOJI_CACHE: dict[str, QPixmap] = {}


def emoji_to_pixmap(emoji: str, size: int = 20) -> QPixmap:
    """
    Convierte un emoji en un QPixmap para usar como DecorationRole.

    ¿Qué hace?
        - Crea un QPixmap transparente de `size x size` píxeles.
        - Dibuja el emoji centrado usando QPainter.
        - Cachea el resultado para reutilizarlo.

    ¿Por qué existe?
        Qt no acepta strings directamente en DecorationRole.
        Necesitamos un QPixmap o QIcon. Esta función encapsula la conversión.

    ¿Por qué cachear?
        El mismo emoji (📁, 📂, 🎮) se usa cientos de veces en el árbol.
        Crear un QPixmap por cada item sería costoso; con caché es instantáneo.
    """
    cache_key = f"{emoji}_{size}"
    if cache_key in _EMOJI_CACHE:
        return _EMOJI_CACHE[cache_key]

    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Usar fuente Segoe UI Emoji (Windows) / Apple Color Emoji (macOS) / Noto Color Emoji (Linux)
    font = QFont("Segoe UI Emoji", int(size * 0.75))
    font.setPointSizeF(size * 0.75)
    painter.setFont(font)

    painter.setPen(Qt.GlobalColor.black)
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, emoji)
    painter.end()

    _EMOJI_CACHE[cache_key] = pixmap
    return pixmap