# ==============================================================================
# * FILTROS: ProxyModel con token_sort_ratio (2 niveles)
# ==============================================================================
# Optimizaciones aplicadas:
#   1. fuzz.token_sort_ratio: maneja palabras reordenadas ("2020 fifa" == "fifa 2020").
#   2. Búsqueda en 2 niveles: franquicias + juegos (no archivos).
#   3. Fast-path substring: evita llamar a rapidfuzz si hay match exacto.
#   4. Debounce 150ms: solo filtra cuando el usuario deja de escribir.
#   5. Caché de textos normalizados: _normalize() se llama UNA vez por item.
#   6. Mapeo item_id -> fila_raíz: lookup O(1) en filterAcceptsRow.
# ==============================================================================

import unicodedata
from PyQt6.QtCore import QSortFilterProxyModel, Qt, QTimer
from rapidfuzz import fuzz


def _normalize(text: str) -> str:
    """
    Normaliza texto eliminando mayúsculas, tildes, guiones y espacios.

    ? Ejemplos:
        "Final Fantasy"  -> "finalfantasy"
        "FIFA 2020"      -> "fifa2020"
        "2020 FIFA"      -> "2020fifa"
        "Pokémon"        -> "pokemon"
        "Metal-Slug"     -> "metalslug"
    """
    if not text:
        return ""
    nfkd = unicodedata.normalize('NFKD', text)
    return ''.join(
        c for c in nfkd
        if unicodedata.category(c) != 'Mn' and c not in '- '
    ).lower()


def _normalize_tokens(text: str) -> str:
    """
    Normaliza Y ordena los tokens alfabéticamente.

    ¿Por qué existe?
        Para que "2020 FIFA" y "FIFA 2020" se vuelvan idénticos al comparar.
        token_sort_ratio de rapidfuzz hace esto internamente, pero necesitamos
        una versión propia para el fast-path substring.

    ? Ejemplos:
        "FIFA 2020"        -> "2020 fifa"
        "2020 FIFA"        -> "2020 fifa"   (idéntico al anterior)
        "Metal Slug 3"     -> "3 metal slug"
        "Final Fantasy 7"  -> "7 final fantasy"
    """
    if not text:
        return ""
    nfkd = unicodedata.normalize('NFKD', text)
    clean = ''.join(
        c for c in nfkd
        if unicodedata.category(c) != 'Mn' and c not in '-'
    ).lower()
    # Ordenar tokens alfabéticamente
    tokens = sorted(clean.split())
    return ' '.join(tokens)


class FuzzyFilterProxyModel(QSortFilterProxyModel):
    """
    Proxy optimizado para búsqueda fuzzy en 2 niveles (franquicias + juegos).

    ^ Flujo de visibilidad:
        - Sin filtro: todo visible.
        - Con filtro: evalúa franquicias (nivel 1) y juegos (nivel 2).
        - Si una franquicia matchea: muestra toda la franquicia.
        - Si un juego matchea: muestra SU franquicia + ese juego + otros juegos visibles.
        - Archivos (nivel 3): heredan visibilidad de su juego padre.
    """

    FUZZY_THRESHOLD = 70  # Bajamos un poco para tolerar más reordenamientos
    DEBOUNCE_MS = 150

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFilterRole(Qt.ItemDataRole.DisplayRole)

        # Estado del filtro
        self._filter_text = ""          # Normalizado sin ordenar (para substring)
        self._filter_tokens = ""        # Normalizado CON tokens ordenados (para token_sort)
        self._pending_text = ""

        # Caché 1: fila_raíz -> texto_normalizado (franquicias)
        self._franchise_texts: dict[int, str] = {}
        # Caché 2: (fila_raíz, fila_juego) -> texto_normalizado (juegos)
        self._game_texts: dict[tuple[int, int], str] = {}
        # Caché 3: id(item) -> fila_raíz
        self._item_to_root_row: dict[int, int] = {}
        # Caché 4: id(item) -> (fila_raíz, fila_juego) [para items de nivel 2 y 3]
        self._item_to_game_key: dict[int, tuple[int, int]] = {}

        # Sets de visibilidad por nivel
        self._visible_franchises: set[int] = set()
        self._visible_games: set[tuple[int, int]] = set()  # (root_row, game_row)

        # Timer de debounce
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(self.DEBOUNCE_MS)
        self._debounce_timer.timeout.connect(self._apply_filter)

    def setSourceModel(self, model):
        """Conecta señales del modelo para invalidar cachés cuando cambian."""
        old_model = self.sourceModel()
        if old_model:
            try:
                old_model.rowsInserted.disconnect(self._invalidate_cache)
                old_model.rowsRemoved.disconnect(self._invalidate_cache)
                old_model.dataChanged.disconnect(self._invalidate_cache)
            except TypeError:
                pass

        super().setSourceModel(model)

        if model:
            model.rowsInserted.connect(self._invalidate_cache)
            model.rowsRemoved.connect(self._invalidate_cache)
            model.dataChanged.connect(self._invalidate_cache)
            self._rebuild_cache()

    def _rebuild_cache(self):
        """
        Pre-calcula textos normalizados para franquicias Y juegos.

        ¿Qué hace?
            - Recorre nivel 1 (franquicias) y nivel 2 (juegos).
            - Ignora nivel 3 (archivos): heredan visibilidad del juego.
            - Mapea cada item a su franquicia raíz.
        """
        self._franchise_texts.clear()
        self._game_texts.clear()
        self._item_to_root_row.clear()
        self._item_to_game_key.clear()

        model = self.sourceModel()
        if not model:
            return

        root = model.invisibleRootItem()
        for fran_row in range(root.rowCount()):
            fran_item = root.child(fran_row)
            if not fran_item:
                continue

            # Caché franquicia
            norm_franchise = _normalize(fran_item.text() or "")
            self._franchise_texts[fran_row] = norm_franchise
            self._item_to_root_row[id(fran_item)] = fran_row

            # Caché juegos dentro de esta franquicia
            for game_row in range(fran_item.rowCount()):
                game_item = fran_item.child(game_row)
                if not game_item:
                    continue

                norm_game = _normalize(game_item.text() or "")
                game_key = (fran_row, game_row)
                self._game_texts[game_key] = norm_game
                self._item_to_root_row[id(game_item)] = fran_row
                self._item_to_game_key[id(game_item)] = game_key

                # Archivos (nivel 3): solo mapeo a franquicia + juego
                for file_row in range(game_item.rowCount()):
                    file_item = game_item.child(file_row)
                    if file_item:
                        self._item_to_root_row[id(file_item)] = fran_row
                        self._item_to_game_key[id(file_item)] = game_key

    def _invalidate_cache(self):
        """Invalida cachés cuando el modelo cambia."""
        self._rebuild_cache()
        if self._filter_text or self._pending_text:
            self._apply_filter()
        else:
            self.invalidateFilter()

    def set_filter_text(self, text: str) -> None:
        """Recibe texto y reinicia debounce."""
        self._pending_text = text.strip()
        self._debounce_timer.start()

    def _apply_filter(self):
        """
        Aplica el filtro tras el debounce.

        ! Algoritmo clave: token_sort_ratio.
        - Ordena las palabras antes de comparar.
        - "2020 fifa" y "FIFA 2020" se vuelven "2020 fifa" ambos.
        - Match perfecto (100%) incluso con palabras reordenadas.
        """
        self._filter_text = _normalize(self._pending_text)
        self._filter_tokens = _normalize_tokens(self._pending_text)
        self._visible_franchises.clear()
        self._visible_games.clear()

        if not self._filter_text:
            # Sin filtro: todo visible
            self._visible_franchises = set(self._franchise_texts.keys())
            self._visible_games = set(self._game_texts.keys())
        else:
            # Evaluar franquicias (nivel 1)
            for fran_row, norm_text in self._franchise_texts.items():
                if self._matches(norm_text):
                    self._visible_franchises.add(fran_row)

            # Evaluar juegos (nivel 2)
            for game_key, norm_text in self._game_texts.items():
                fran_row, _ = game_key
                if self._matches(norm_text):
                    # Marcar juego Y su franquicia como visibles
                    self._visible_games.add(game_key)
                    self._visible_franchises.add(fran_row)

        self.invalidateFilter()

    def _matches(self, norm_text: str) -> bool:
        """
        Verifica coincidencia con fast-path + token_sort_ratio.

        ¿Por qué token_sort_ratio?
            - ratio("2020 fifa", "fifa 2020") = 50% (penaliza orden)
            - partial_ratio("2020fifa", "fifa2020") = 50% (no es substring)
            - token_sort_ratio("2020 fifa", "FIFA 2020") = 100% (ordena tokens)

        ! Esto resuelve el bug de "2020 FIFA" vs "FIFA 2020".
        """
        if not self._filter_text:
            return True

        # Fast-path 1: substring exacto en texto sin ordenar
        if self._filter_text in norm_text:
            return True

        # Fast-path 2: substring en versión con tokens ordenados
        norm_tokens = _normalize_tokens(norm_text)
        if self._filter_tokens in norm_tokens:
            return True

        # Slow-path: token_sort_ratio para tolerancia fuzzy
        score = fuzz.token_sort_ratio(self._filter_text, norm_text) * 100
        return score >= self.FUZZY_THRESHOLD

    def filterAcceptsRow(self, source_row: int, source_parent) -> bool:
        """
        Decide visibilidad con lookup O(1) en cachés.

        ^ Reglas de visibilidad:
            - Franquicia (nivel 1): visible si está en _visible_franchises.
            - Juego (nivel 2): visible si está en _visible_games.
            - Archivo (nivel 3): visible si su juego padre es visible.
        """
        if not self._filter_text:
            return True

        model = self.sourceModel()

        # ------------------------------------------------------------------
        # * Caso: Nodo con padre (juego o archivo)
        # ------------------------------------------------------------------
        if source_parent.isValid():
            index = model.index(source_row, 0, source_parent)
            item = model.itemFromIndex(index)
            if item is None:
                return False

            # Si es un juego (nivel 2): lookup en _visible_games
            game_key = self._item_to_game_key.get(id(item))
            if game_key is not None:
                return game_key in self._visible_games

            # Si es un archivo (nivel 3): su visibilidad depende del juego padre
            # Obtenemos el item padre y verificamos si el juego está visible
            parent_item = model.itemFromIndex(source_parent)
            if parent_item is None:
                return False
            parent_game_key = self._item_to_game_key.get(id(parent_item))
            if parent_game_key is None:
                return False
            return parent_game_key in self._visible_games

        # ------------------------------------------------------------------
        # * Caso: Nodo raíz (franquicia)
        # ------------------------------------------------------------------
        return source_row in self._visible_franchises