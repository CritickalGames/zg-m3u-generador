from PyQt6.QtGui import QShortcut, QKeySequence, QStandardItemModel, QUndoStack
from PyQt6.QtWidgets import QWidget, QTreeView
from typing import Callable, Optional

from .tree_editor import (
    undo_action, redo_action, delete_selected,
    cut_selected, paste_nodes
)


def setup_edit_shortcuts(
    parent: QWidget,
    model: QStandardItemModel,
    undo_stack: QUndoStack,
    tree_view: QTreeView,
    on_status: Callable[[str], None],
    proxy_model=None  # ! Necesario para operaciones con filtro activo
) -> None:
    """
    Registra los atajos de teclado globales de edición.

    ¿Qué hace?
        - Ctrl+Z -> undo
        - Ctrl+Y -> redo
        - Ctrl+X -> cut_selected
        - Ctrl+V -> paste_nodes
        - Supr   -> delete_selected

    ¿Por qué recibe proxy_model?
        Cuando hay una búsqueda activa, los índices del tree_view son del proxy.
        Para operar sobre el modelo fuente, hay que mapearlos con mapToSource.
    """
    # ------------------------------------------------------------------
    # * ↩️ Ctrl+Z: Deshacer
    # ------------------------------------------------------------------
    undo_shortcut = QShortcut(QKeySequence.StandardKey.Undo, parent)
    undo_shortcut.activated.connect(lambda: undo_action(undo_stack, on_status))

    # ------------------------------------------------------------------
    # * ↪️ Ctrl+Y: Rehacer
    # ------------------------------------------------------------------
    redo_shortcut = QShortcut(QKeySequence.StandardKey.Redo, parent)
    redo_shortcut.activated.connect(lambda: redo_action(undo_stack, on_status))

    # ------------------------------------------------------------------
    # * ✂️ Ctrl+X: Cortar
    # ------------------------------------------------------------------
    cut_shortcut = QShortcut(QKeySequence.StandardKey.Cut, parent)
    cut_shortcut.activated.connect(
        lambda: cut_selected(tree_view, model, undo_stack, on_status, proxy_model)
    )

    # ------------------------------------------------------------------
    # * 📋 Ctrl+V: Pegar
    # ------------------------------------------------------------------
    paste_shortcut = QShortcut(QKeySequence.StandardKey.Paste, parent)
    paste_shortcut.activated.connect(
        lambda: paste_nodes(tree_view, model, undo_stack, on_status, proxy_model)
    )

    # ------------------------------------------------------------------
    # * 🗑️ Supr: Eliminar selección
    # ------------------------------------------------------------------
    delete_shortcut = QShortcut(QKeySequence.StandardKey.Delete, parent)
    delete_shortcut.activated.connect(
        lambda: delete_selected(tree_view, model, undo_stack, on_status, proxy_model)
    )