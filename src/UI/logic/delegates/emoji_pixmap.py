from PyQt6.QtGui import QPixmap, QFont, QPainter, QColor
from PyQt6.QtCore import QSize, Qt

def emoji_a_pixmap(emoji, tamanyo=24):
    tamano = QSize(tamanyo, tamanyo)
    pixmap = QPixmap(tamano)
    pixmap.fill(QColor(0, 0, 0, 0))
    _dibujar_emoji_en_pixmap(pixmap, emoji, tamanyo)
    return pixmap

def _dibujar_emoji_en_pixmap(pixmap, emoji, tamanyo):
    pintor = QPainter(pixmap)
    pintor.setRenderHint(QPainter.RenderHint.TextAntialiasing)
    fuente = QFont("Segoe UI Emoji", int(tamanyo * 0.75))
    pintor.setFont(fuente)
    pintor.setPen(QColor(0, 0, 0))
    pintor.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, emoji)
    pintor.end()