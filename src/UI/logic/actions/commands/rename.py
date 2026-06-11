from PyQt6.QtGui import QUndoCommand

class ComandoRenombrar(QUndoCommand):
    def __init__(self, nodo, nombre_nuevo):
        super().__init__("Renombrar")
        self._nodo = nodo
        self._nombre_nuevo = nombre_nuevo
        self._nombre_anterior = nodo.text()

    def redo(self):
        self._nodo.setText(self._nombre_nuevo)

    def undo(self):
        self._nodo.setText(self._nombre_anterior)