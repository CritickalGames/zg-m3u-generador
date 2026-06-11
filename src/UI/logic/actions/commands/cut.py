from PyQt6.QtGui import QUndoCommand

class ComandoCortar(QUndoCommand):
    def __init__(self, modelo, nodos):
        super().__init__("Cortar")
        self._modelo = modelo
        self._nodos = nodos
        self._padres = [(n.parent() or modelo.invisibleRootItem(), n.row()) for n in nodos]

    def redo(self):
        for padre, fila in reversed(self._padres):
            padre.takeRow(fila)

    def undo(self):
        for (padre, fila), nodo in zip(self._padres, self._nodos):
            padre.insertRow(fila, nodo)