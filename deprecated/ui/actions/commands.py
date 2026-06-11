# ==============================================================================
# * COMANDOS DE EDICIÓN (QUndoCommand)
# ==============================================================================
# - Cada clase representa una acción reversible sobre el modelo.
# - PyQt6 requiere heredar de QUndoCommand e implementar redo() y undo().
# - El texto del comando se usa para etiquetas en menús o tooltips.
#
# ^ Filosofía: Los comandos son la única forma válida de mutar el modelo
#   cuando se usa QUndoStack. Nunca llamar a model.setData() directamente.
# ==============================================================================

from PyQt6.QtGui import QUndoCommand, QStandardItemModel, QStandardItem
from PyQt6.QtCore import QModelIndex
from deprecated.ui.actions.clipboard import clipboard


class RenameNodeCommand(QUndoCommand):
    def __init__(self, item, old_text, new_text, parent=None):
        super().__init__(f"Renombrar '{old_text}' → '{new_text}'", parent)
        self.item = item
        self.old_text = old_text
        self.new_text = new_text

    def redo(self):
        # ! Bloquear señales para evitar que itemChanged se dispare y cree otro comando
        self.item.model().blockSignals(True)
        self.item.setText(self.new_text)
        self.item.model().blockSignals(False)

    def undo(self):
        self.item.model().blockSignals(True)
        self.item.setText(self.old_text)
        self.item.model().blockSignals(False)

class RemoveNodesCommand(QUndoCommand):
    """
    Comando para eliminar uno o más nodos del árbol lógico.

    ¿Qué hace?
        - redo(): Extrae las filas del modelo usando takeRow() (conserva hijos).
        - undo(): Reinserta las filas extraídas en su posición original.

    ¿Por qué usa takeRow() en lugar de removeRow() + clone()?
        ! BUG CRÍTICO: QStandardItem.clone() NO clona los hijos recursivamente.
        Si borrabas una franquicia con 5 juegos, al hacer undo volvía la
        franquicia vacía. takeRow() extrae la fila COMPLETA (con todos sus
        descendientes) y permite reinsertarla intacta.

    ? Flujo de estado:
        - Constructor: guarda referencias al modelo y filas a eliminar.
        - Primer redo(): extrae items del modelo y los almacena en items_storage.
        - undo(): reinserta los items desde items_storage al modelo.
        - Redos subsecuentes: vuelve a extraer (descartando el resultado,
          porque items_storage ya contiene los datos originales).
    """

    def __init__(
        self,
        model: QStandardItemModel,
        parent_index: QModelIndex,
        rows: list[int],
        description: str = "Eliminar elementos",
        parent=None
    ):
        super().__init__(description, parent)
        self.model = model
        self.parent_index = parent_index
        # Ordenar ascendente para reinsertar en orden correcto durante undo
        self.rows = sorted(rows)
        # Almacena los items extraídos (con todos sus hijos) entre redo/undo
        self.items_storage: list[tuple[int, list[QStandardItem]]] = []
        # Flag para distinguir el primer redo (extracción) de los siguientes
        self._first_redo_done = False

    def redo(self):
        """Extrae las filas del modelo, conservando la jerarquía de hijos."""
        if not self._first_redo_done:
            # Primera ejecución: extraer y GUARDAR los items
            for row in reversed(self.rows):  # Reversa para evitar desfase de índices
                items = self._take_row(row)
                # Insertar al inicio para mantener orden ascendente en storage
                self.items_storage.insert(0, (row, items))
            self._first_redo_done = True
        else:
            # Redos subsecuentes: solo remover (los items ya están en storage)
            for row in reversed(self.rows):
                self._take_row(row)  # Extraer y descartar

    def undo(self):
        """Reinserta las filas previamente extraídas con toda su jerarquía."""
        for row, items in self.items_storage:
            self._insert_row(row, items)

    def _take_row(self, row: int) -> list[QStandardItem]:
        """Extrae una fila del modelo (con todos sus hijos) y la devuelve."""
        if self.parent_index.isValid():
            parent_item = self.model.itemFromIndex(self.parent_index)
            return parent_item.takeRow(row)
        return self.model.takeRow(row)

    def _insert_row(self, row: int, items: list[QStandardItem]):
        """Reinserta una fila completa (con hijos) en el modelo."""
        if self.parent_index.isValid():
            parent_item = self.model.itemFromIndex(self.parent_index)
            parent_item.insertRow(row, items)
        else:
            self.model.insertRow(row, items)
            
class MoveNodeCommand(QUndoCommand):
    """
    Comando para mover un nodo dentro del árbol (drag & drop).

    ¿Qué hace?
        - Almacena origen (padre + fila) y destino (padre + fila).
        - redo(): Mueve la fila al destino.
        - undo(): Mueve la fila de vuelta al origen.

    ¿Por qué existe?
        El drag & drop nativo de QTreeView NO se registra automáticamente
        en QUndoStack. Debemos interceptarlo y crear este comando manualmente.
    """

    def __init__(
        self,
        model: QStandardItemModel,
        source_parent: QModelIndex,
        source_row: int,
        dest_parent: QModelIndex,
        dest_row: int,
        parent=None
    ):
        super().__init__("Mover elemento", parent)
        self.model = model
        self.source_parent = source_parent
        self.source_row = source_row
        self.dest_parent = dest_parent
        self.dest_row = dest_row

    def redo(self):
        self.model.moveRow(
            self.source_parent, self.source_row,
            self.dest_parent, self.dest_row
        )

    def undo(self):
        # ! Al deshacer, el destino se convierte en origen y viceversa
        # - Ajustar fila de destino porque moveRow inserta ANTES de dest_row
        adjusted_row = self.source_row
        if self.source_parent == self.dest_parent and self.dest_row < self.source_row:
            adjusted_row += 1
        self.model.moveRow(
            self.dest_parent, self.dest_row - 1 if self.dest_row > 0 else 0,
            self.source_parent, adjusted_row
        )

class CutNodesCommand(QUndoCommand):
    """
    Comando para cortar nodos (Ctrl+X).

    ¿Qué hace?
        - redo(): Extrae las filas del modelo y las guarda en el clipboard.
        - undo(): Reinserta las filas desde el clipboard al modelo.

    ¿Por qué es distinto a RemoveNodesCommand?
        RemoveNodesCommand descarta los items. CutNodesCommand los preserva
        en el clipboard para poder pegarlos después en otra posición.

    ? Flujo típico:
        1. Usuario selecciona nodos y pulsa Ctrl+X
        2. CutNodesCommand.extrae los nodos y los guarda en clipboard
        3. Usuario navega a otra franquicia
        4. Usuario pulsa Ctrl+V
        5. PasteNodesCommand clona desde clipboard e inserta
    """

    def __init__(
        self,
        model: QStandardItemModel,
        parent_index: QModelIndex,
        rows: list[int],
        description: str = "Cortar elementos",
        parent=None
    ):
        super().__init__(description, parent)
        self.model = model
        self.parent_index = parent_index
        self.rows = sorted(rows)
        self.cut_items: list[list[QStandardItem]] = []
        self._first_redo_done = False

    def redo(self):
        if not self._first_redo_done:
            # Extraer filas y guardarlas en el clipboard
            for row in reversed(self.rows):
                items = self._take_row(row)
                self.cut_items.insert(0, items)
            clipboard.set_items(self.cut_items)
            self._first_redo_done = True
        else:
            # Redos subsecuentes: solo remover (items ya están en clipboard)
            for row in reversed(self.rows):
                self._take_row(row)

    def undo(self):
        # Reinsertar desde el storage local (no del clipboard,
        # porque el usuario pudo haber cortado otra cosa después)
        parent_item = (
            self.model.itemFromIndex(self.parent_index)
            if self.parent_index.isValid()
            else self.model.invisibleRootItem()
        )
        for row, items in zip(self.rows, self.cut_items):
            parent_item.insertRow(row, items)

    def _take_row(self, row: int) -> list[QStandardItem]:
        if self.parent_index.isValid():
            parent_item = self.model.itemFromIndex(self.parent_index)
            return parent_item.takeRow(row)
        return self.model.takeRow(row)


class PasteNodesCommand(QUndoCommand):
    """
    Comando para pegar nodos desde el clipboard (Ctrl+V).

    ¿Qué hace?
        - redo(): Clona los items del clipboard y los inserta en el destino.
        - undo(): Remueve los items recién insertados.

    ¿Por qué clona en lugar de mover?
        Porque el clipboard debe conservar su contenido para permitir
        múltiples pegados (Ctrl+V repetidos). Mover destruiría el buffer.

    ? Destino de pegado:
        - Si hay un nodo seleccionado: se pega COMO HIJO del nodo.
        - Si no hay selección: se pega en la raíz (nivel de franquicia).
    """

    def __init__(
        self,
        model: QStandardItemModel,
        dest_parent_index: QModelIndex,
        parent=None
    ):
        super().__init__("Pegar elementos", parent)
        self.model = model
        self.dest_parent_index = dest_parent_index
        # Guardamos una referencia a los items clonados para poder deshacer
        self.pasted_items: list[list[QStandardItem]] = []
        self._first_redo_done = False

    def redo(self):
        if not clipboard.has_content():
            return

        parent_item = (
            self.model.itemFromIndex(self.dest_parent_index)
            if self.dest_parent_index.isValid()
            else self.model.invisibleRootItem()
        )

        if not self._first_redo_done:
            # Primera vez: clonar desde el clipboard
            for source_row in clipboard.get_items():
                cloned_row = [item.clone() for item in source_row]
                parent_item.appendRow(cloned_row)
                self.pasted_items.append(cloned_row)
            self._first_redo_done = True
        else:
            # Redos subsecuentes: reinsertar los mismos clones
            for cloned_row in self.pasted_items:
                parent_item.appendRow(cloned_row)

    def undo(self):
        # Remover las filas pegadas (de atrás hacia adelante)
        parent_item = (
            self.model.itemFromIndex(self.dest_parent_index)
            if self.dest_parent_index.isValid()
            else self.model.invisibleRootItem()
        )
        # Las filas pegadas están al final del padre
        total_rows = parent_item.rowCount()
        num_pasted = len(self.pasted_items)
        for _ in range(num_pasted):
            parent_item.takeRow(total_rows - 1)
            total_rows -= 1