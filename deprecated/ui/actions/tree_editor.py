# ==============================================================================
# * LÓGICA DE EDICIÓN DEL ÁRBOL (Con QUndoStack)
# ==============================================================================
# - Todas las mutaciones pasan por QUndoStack.push().
# - Esto garantiza que cada acción sea reversible.
# - Las funciones reciben el stack como dependencia inyectada.
# ==============================================================================

from PyQt6.QtGui import QStandardItemModel, QUndoStack
from PyQt6.QtWidgets import QTreeView
from typing import Callable, Optional

from .commands import RemoveNodesCommand, CutNodesCommand, PasteNodesCommand


def undo_action(
    undo_stack: QUndoStack,
    on_status: Optional[Callable[[str], None]] = None
) -> None:
    """
    Deshace la última acción registrada en el stack.

    ¿Qué hace?
        - Invoca undo_stack.undo() si hay acciones disponibles.
        - Notifica el resultado vía callback on_status.

    ¿Por qué recibe QUndoStack en vez de QStandardItemModel?
        Porque en PyQt6 el historial vive en el stack, no en el modelo.
        El stack es quien conoce el estado actual del historial.
    """
    if undo_stack.canUndo():
        undo_stack.undo()
        if on_status:
            on_status(f"↩️ Deshecho: {undo_stack.undoText()}")
    else:
        if on_status:
            on_status("⚠️ Nada que deshacer")


def redo_action(
    undo_stack: QUndoStack,
    on_status: Optional[Callable[[str], None]] = None
) -> None:
    """
    Rehace la última acción deshecha en el stack.

    ¿Qué hace?
        - Invoca undo_stack.redo() si hay acciones en la pila de rehacer.
        - Notifica el resultado vía callback on_status.
    """
    if undo_stack.canRedo():
        undo_stack.redo()
        if on_status:
            on_status(f"↪️ Rehecho: {undo_stack.redoText()}")
    else:
        if on_status:
            on_status("⚠️ Nada que rehacer")


def delete_selected(
    tree_view: QTreeView,
    model: QStandardItemModel,
    undo_stack: QUndoStack,
    on_status: Optional[Callable[[str], None]] = None,
    proxy_model=None
) -> None:
    selected_indexes = tree_view.selectionModel().selectedIndexes()
    if not selected_indexes:
        if on_status:
            on_status("⚠️ No hay elementos seleccionados")
        return

    # ! Mapear índices si hay proxy activo
    if proxy_model is not None:
        selected_indexes = [proxy_model.mapToSource(idx) for idx in selected_indexes]

    from collections import defaultdict
    rows_by_parent: dict = defaultdict(list)
    for idx in selected_indexes:
        rows_by_parent[idx.parent()].append(idx.row())

    for parent_index, rows in rows_by_parent.items():
        unique_rows = sorted(set(rows), reverse=True)
        cmd = RemoveNodesCommand(
            model=model,
            parent_index=parent_index,
            rows=unique_rows,
            description=f"Eliminar {len(unique_rows)} elemento(s)"
        )
        undo_stack.push(cmd)

    if on_status:
        total = sum(len(set(r)) for r in rows_by_parent.values())
        on_status(f"🗑️ {total} elemento(s) eliminado(s). Ctrl+Z para deshacer.")

def cut_selected(
    tree_view: QTreeView,
    model: QStandardItemModel,
    undo_stack: QUndoStack,
    on_status: Optional[Callable[[str], None]] = None,
    proxy_model=None  # ! Necesario para mapear índices si hay filtro activo
) -> None:
    """
    Corta los nodos seleccionados al clipboard interno.

    ¿Qué hace?
        - Obtiene índices seleccionados (del proxy si existe).
        - Los mapea al modelo fuente si hay proxy activo.
        - Crea CutNodesCommand y lo pushea al stack.
    """
    selected_indexes = tree_view.selectionModel().selectedIndexes()
    if not selected_indexes:
        if on_status:
            on_status("⚠️ No hay elementos seleccionados para cortar")
        return

    # Mapear índices del proxy al modelo fuente si es necesario
    if proxy_model is not None:
        selected_indexes = [proxy_model.mapToSource(idx) for idx in selected_indexes]

    from collections import defaultdict
    rows_by_parent: dict = defaultdict(list)
    for idx in selected_indexes:
        rows_by_parent[idx.parent()].append(idx.row())

    for parent_index, rows in rows_by_parent.items():
        unique_rows = sorted(set(rows), reverse=True)
        cmd = CutNodesCommand(
            model=model,
            parent_index=parent_index,
            rows=unique_rows,
            description=f"Cortar {len(unique_rows)} elemento(s)"
        )
        undo_stack.push(cmd)

    if on_status:
        total = sum(len(set(r)) for r in rows_by_parent.values())
        on_status(f"✂️ {total} elemento(s) cortado(s). Ctrl+V para pegar.")


def paste_nodes(
    tree_view: QTreeView,
    model: QStandardItemModel,
    undo_stack: QUndoStack,
    on_status: Optional[Callable[[str], None]] = None,
    proxy_model=None
) -> None:
    """
    Pega los items del clipboard como hijos del nodo seleccionado.

    ¿Qué hace?
        - Verifica que el clipboard tenga contenido.
        - Determina el destino: nodo seleccionado o raíz.
        - Crea PasteNodesCommand y lo pushea al stack.
    """
    if not clipboard.has_content():
        if on_status:
            on_status("⚠️ El portapapeles está vacío")
        return

    # Determinar destino: nodo seleccionado o raíz
    current = tree_view.currentIndex()
    if current.isValid() and proxy_model is not None:
        current = proxy_model.mapToSource(current)

    dest_parent_index = current.parent() if current.isValid() else QModelIndex()

    cmd = PasteNodesCommand(
        model=model,
        dest_parent_index=dest_parent_index,
        description="Pegar elementos"
    )
    undo_stack.push(cmd)

    if on_status:
        on_status("📋 Elementos pegados. Ctrl+Z para deshacer.")