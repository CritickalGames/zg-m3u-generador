from PyQt6.QtCore import QSortFilterProxyModel, Qt, QModelIndex
from rapidfuzz import fuzz

class FiltroFuzzyProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._umbral = 85
        self._texto_busqueda = ""

    def set_texto_busqueda(self, texto: str):
        self._texto_busqueda = texto.lower().strip()
        self.invalidateFilter() # Fuerza a reevaluar todo el árbol

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        # Si no hay búsqueda, mostrar todo
        if not self._texto_busqueda:
            return True
        
        modelo_origen = self.sourceModel()
        indice = modelo_origen.index(source_row, 0, source_parent)
        
        # 1. Comprobar si el elemento actual coincide
        texto_item = str(modelo_origen.data(indice, Qt.ItemDataRole.DisplayRole)).lower()
        if fuzz.partial_ratio(self._texto_busqueda, texto_item) >= self._umbral:
            return True
        
        # 2. Comprobar si algún hijo coincide (para mantener visible a los padres)
        if modelo_origen.hasChildren(indice):
            for i in range(modelo_origen.rowCount(indice)):
                if self.filterAcceptsRow(i, indice):
                    return True
        
        return False