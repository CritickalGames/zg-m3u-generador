from PyQt6.QtGui import QUndoStack, QStandardItem
from PyQt6.QtCore import Qt
from UI.logic.actions.clipboard import PortapapelesInterno
from UI.logic.actions.commands.rename import ComandoRenombrar
from UI.logic.actions.commands.remove import ComandoEliminar
from UI.logic.actions.commands.cut import ComandoCortar
from UI.logic.actions.commands.paste import ComandoPegar

class EditorArbol:
    def __init__(self, vista, modelo_fuente, portapapeles):
        self._vista = vista
        self._modelo_fuente = modelo_fuente
        self._portapapeles = portapapeles
        self._pila = QUndoStack()

    def deshacer(self):
        if self._pila.canUndo():
            self._pila.undo()

    def rehacer(self):
        if self._pila.canRedo():
            self._pila.redo()

    def cortar(self):
        nodos = self._obtener_nodos_fuente_seleccionados()
        if nodos:
            self._portapapeles.guardar_corte(nodos)
            self._pila.push(ComandoCortar(self._modelo_fuente, nodos))

    def copiar(self):
        nodos = self._obtener_nodos_fuente_seleccionados()
        if nodos:
            self._portapapeles.guardar_copia(nodos)

    def pegar(self):
        if self._portapapeles.esta_vacio():
            return
        destino = self._obtener_destino_fuente()
        if destino:
            self._pila.push(ComandoPegar(destino, self._portapapeles.obtener_nodos(), self._portapapeles.obtener_modo()))

    def eliminar(self):
        nodos = self._obtener_nodos_fuente_seleccionados()
        if nodos:
            self._pila.push(ComandoEliminar(self._modelo_fuente, nodos))

    def renombrar(self):
        indices = self._vista.selectedIndexes()
        if indices:
            # Mapear al modelo fuente para editar
            proxy_index = indices[0]
            if proxy_index.column() == 0:
                source_index = self._vista.model().mapToSource(proxy_index)
                self._vista.edit(source_index)

    def _obtener_nodos_fuente_seleccionados(self):
        indices = self._vista.selectedIndexes()
        proxy_model = self._vista.model()
        nodos = []
        for i in indices:
            if i.column() == 0:
                source_index = proxy_model.mapToSource(i)
                item = self._modelo_fuente.itemFromIndex(source_index)
                if item and item not in nodos:
                    nodos.append(item)
        return nodos

    def _obtener_destino_fuente(self):
        indices = self._vista.selectedIndexes()
        if not indices:
            return self._modelo_fuente.invisibleRootItem()
        
        proxy_model = self._vista.model()
        source_index = proxy_model.mapToSource(indices[0])
        item = self._modelo_fuente.itemFromIndex(source_index)
        return item if item else self._modelo_fuente.invisibleRootItem()