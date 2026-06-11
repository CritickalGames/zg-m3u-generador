from PyQt6.QtGui import QUndoCommand, QStandardItem

class ComandoPegar(QUndoCommand):
    def __init__(self, destino, nodos):
        super().__init__("Pegar")
        self._destino = destino
        self._copias = [_clonar_nodo(n) for n in nodos]

    def redo(self):
        for copia in self._copias:
            self._destino.appendRow(copia)

    def undo(self):
        for _ in self._copias:
            self._destino.removeRow(self._destino.rowCount() - 1)

def _clonar_nodo(nodo):
    copia = QStandardItem(nodo.text())
    copia.setEditable(nodo.isEditable())
    for clave in nodo.data(0x0101) and [0x0101, 0x0102]:
        copia.setData(nodo.data(clave), clave)
    for i in range(nodo.rowCount()):
        copia.appendRow(_clonar_nodo(nodo.child(i)))
    return copia