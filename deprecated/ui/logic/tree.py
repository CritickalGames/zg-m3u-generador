# ==============================================================================
# * CONSTRUCTOR DEL ÁRBOL LÓGICO (populate_tree)
# ==============================================================================
# - Construye el árbol de franquicias -> juegos -> versiones.
# - Los emojis se asignan vía DecorationRole (nativo de Qt).
# - El texto en DisplayRole permanece limpio (sin emojis).
#
# ^ Filosofía: Separar datos de presentación.
#   Qt se encarga de pintar el icono a la izquierda del texto automáticamente.
# ==============================================================================

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItem
from grouper.sorting import custom_sort_key
from deprecated.ui.widgets.delegates import emoji_to_pixmap  # ! Helper de conversión emoji -> QPixmap


def populate_tree(model, rom_data: dict):
    """
    Construye el árbol lógico de franquicias/juegos/versiones.

    ¿Qué hace?
        - Crea QStandardItems con el NOMBRE LIMPIO en DisplayRole.
        - Asigna el emoji como DecorationRole (icono nativo de Qt).
        - Aplica el ordenamiento personalizado a cada nivel.

    ¿Por qué usa DecorationRole?
        ! Clave: Qt pinta nativamente el icono a la izquierda del texto.
        Esto mantiene:
            - Selección azul nativa al hacer clic
            - Efecto hover nativo
            - Editor inline limpio al pulsar F2 (solo edita el texto)
            - Texto limpio para exportar a .m3u sin regex

    ¿Cómo se conecta con el flujo general?
        Es invocado por scan_and_populate() tras la agrupación fuzzy.
        El modelo resultante es la fuente de verdad para generate_m3u().
    """
    root = model.invisibleRootItem()
    model.setHorizontalHeaderLabels(["Nombre / Estructura"])

    # ------------------------------------------------------------------
    # * Nivel 1: Franquicias
    # ------------------------------------------------------------------
    sorted_franchises = sorted(rom_data.keys(), key=custom_sort_key)

    for franchise in sorted_franchises:
        fran_item = QStandardItem(franchise)  # ! Texto limpio
        fran_item.setData(emoji_to_pixmap("📁"), Qt.ItemDataRole.DecorationRole)
        fran_item.setEditable(True)
        fran_item.setData("franchise", Qt.ItemDataRole.UserRole)

        games = rom_data[franchise]
        sorted_games = sorted(games.keys(), key=custom_sort_key)

        # --------------------------------------------------------------
        # * Nivel 2: Juegos dentro de cada franquicia
        # --------------------------------------------------------------
        for game in sorted_games:
            game_item = QStandardItem(game)  # ! Texto limpio
            game_item.setData(emoji_to_pixmap("🎮"), Qt.ItemDataRole.DecorationRole)
            game_item.setEditable(True)
            game_item.setData("game", Qt.ItemDataRole.UserRole)

            sorted_files = sorted(games[game], key=lambda x: custom_sort_key(x.name))

            # ----------------------------------------------------------
            # * Nivel 3: Versiones/Archivos dentro de cada juego
            # ----------------------------------------------------------
            for file_path in sorted_files:
                file_item = QStandardItem(file_path.name)  # ! Texto limpio
                file_item.setData(emoji_to_pixmap("💿"), Qt.ItemDataRole.DecorationRole)
                file_item.setEditable(False)
                file_item.setData(str(file_path), Qt.ItemDataRole.UserRole)
                game_item.appendRow(file_item)

            fran_item.appendRow(game_item)

        root.appendRow(fran_item)