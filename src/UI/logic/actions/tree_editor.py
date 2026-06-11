from PyQt6.QtGui import QUndoStack

class EditorArbol:
    def __init__(self, vista, portapapeles):
        self._vista = vista
        self._portapapeles = portapapeles
        self._pila = QUndoStack()

    def deshacer(self):
        if self._pila.canUndo():
            self._pila.undo()

    def rehacer(self):
        if self._pila.canRedo():
            self._pila.redo()

    def cortar(self):
        nodos = self._obtener_nodos_seleccionados()
        if nodos:
            self._portapapeles.guardar_corte(nodos)

    def pegar(self):
        if self._portapapeles.esta_vacio():
            return
        destino = self._obtener_destino()
        if destino:
            _ejecutar_pegado(self._pila, self._vista, self._portapapeles, destino)

    def eliminar(self):
        nodos = self._obtener_nodos_seleccionados()
        if nodos:
            _ejecutar_eliminacion(self._pila, self._vista, nodos)

    def renombrar(self):
        indices = self._vista.selectedIndexes()
        if indices:
            self._vista.edit(indices[0])

    def _obtener_nodos_seleccionados(self):
        indices = self._vista.selectedIndexes()
        modelo = self._vista.model()
        nodos = [modelo.itemFromIndex(i) for i in indices if i.column() == 0]
        return nodos

    def _obtener_destino(self):
        indices = self._vista.selectedIndexes()
        if not indices:
            return self._vista.model().invisibleRootItem()
        modelo = self._vista.model()
        return modelo.itemFromIndex(indices[0])

def _ejecutar_pegado(pila, vista, portapapeles, destino):
    pass

def _ejecutar_eliminacion(pila, vista, nodos):
    pass