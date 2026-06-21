from PyQt6.QtGui import QUndoCommand, QStandardItem
from PyQt6.QtCore import Qt

class ComandoPegar(QUndoCommand):
    def __init__(self, destino, nodos, modo):
        super().__init__("Pegar")
        self._destino = destino
        self._modo = modo
        self._copias = [_clonar_nodo(n) for n in nodos]
        self._filas_insertadas = []

    def redo(self):
        self._filas_insertadas = []
        for copia in self._copias:
            fila = self._destino.rowCount()
            self._destino.appendRow(copia)
            self._filas_insertadas.append(fila)

    def undo(self):
        for fila in reversed(self._filas_insertadas):
            self._destino.removeRow(fila)

def _clonar_nodo(nodo):
    copia = QStandardItem(nodo.text())
    copia.setEditable(nodo.isEditable())
    for rol in [Qt.ItemDataRole.UserRole, Qt.ItemDataRole.UserRole + 1]:
        dato = nodo.data(rol)
        if dato is not None:
            copia.setData(dato, rol)
    
    for i in range(nodo.rowCount()):
        copia.appendRow(_clonar_nodo(nodo.child(i)))
    return copia