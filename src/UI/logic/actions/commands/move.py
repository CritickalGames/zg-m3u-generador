from PyQt6.QtGui import QUndoCommand

class ComandoMover(QUndoCommand):
    def __init__(self, modelo, nodos, destino):
        super().__init__("Mover")
        self._modelo = modelo
        self._nodos = nodos
        self._destino = destino
        self._origenes = [(n.parent() or modelo.invisibleRootItem(), n.row()) for n in nodos]

    def redo(self):
        for padre, fila in reversed(self._origenes):
            nodo = padre.takeRow(fila)
            self._destino.appendRow(nodo)

    def undo(self):
        for (padre, fila), nodo in zip(reversed(self._origenes), reversed(self._nodos)):
            self._destino.takeRow(self._destino.rowCount() - 1)
            padre.insertRow(fila, nodo)