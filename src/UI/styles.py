def aplicar_estilo_global(app):
    paleta = _obtener_paleta()
    qss = _construir_qss(paleta)
    _aplicar_a_app(app, qss)

def _obtener_paleta():
    paleta = {
        "fondo_principal": "#1e1e2e",
        "fondo_secundario": "#313244",
        "fondo_terciario": "#45475a",
        "texto_principal": "#cdd6f4",
        "texto_secundario": "#a6adc8",
        "acento": "#89b4fa",
        "acento_hover": "#b4befe",
        "exito": "#a6e3a1",
        "error": "#f38ba8",
        "borde": "#585b70",
    }
    return paleta

def _construir_qss(p):
    qss = _estilo_base(p) + _estilo_botones(p) + _estilo_inputs(p)
    qss += _estilo_trees(p) + _estilo_labels(p) + _estilo_splitter(p)
    qss += _estilo_status_bar(p) + _estilo_scrollbars(p)
    return qss

def _aplicar_a_app(app, qss):
    app.setStyleSheet(qss)

def _estilo_base(p):
    return f"""
    QMainWindow, QWidget {{
        background-color: {p['fondo_principal']};
        color: {p['texto_principal']};
    }}
    """

def _estilo_botones(p):
    return f"""
    QPushButton {{
        background-color: {p['fondo_secundario']};
        color: {p['texto_principal']};
        border: 1px solid {p['borde']};
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 600;
        min-width: 90px;
    }}
    QPushButton:hover {{
        background-color: {p['fondo_terciario']};
        border-color: {p['acento']};
        color: {p['acento']};
    }}
    QPushButton:pressed {{
        background-color: {p['acento']};
        color: {p['fondo_principal']};
    }}
    QPushButton:disabled {{
        background-color: {p['fondo_principal']};
        color: {p['texto_secundario']};
        border-color: {p['borde']};
    }}
    """

def _estilo_inputs(p):
    return f"""
    QLineEdit {{
        background-color: {p['fondo_secundario']};
        color: {p['texto_principal']};
        border: 1px solid {p['borde']};
        border-radius: 6px;
        padding: 8px 12px;
        selection-background-color: {p['acento']};
        selection-color: {p['fondo_principal']};
    }}
    QLineEdit:focus {{
        border-color: {p['acento']};
    }}
    QLineEdit::placeholder {{
        color: {p['texto_secundario']};
    }}
    """

def _estilo_trees(p):
    return f"""
    QTreeView {{
        background-color: {p['fondo_secundario']};
        color: {p['texto_principal']};
        border: 1px solid {p['borde']};
        border-radius: 6px;
        padding: 6px;
        alternate-background-color: {p['fondo_principal']};
        outline: none;
    }}
    QTreeView::item {{
        padding: 4px 8px;
        border-radius: 4px;
        margin: 1px 0px;
    }}
    QTreeView::item:hover {{
        background-color: {p['fondo_terciario']};
    }}
    QTreeView::item:selected {{
        background-color: {p['acento']};
        color: {p['fondo_principal']};
        font-weight: 600;
    }}
    QTreeView::branch {{
        background-color: transparent;
    }}
    QTreeView::branch:has-children:!has-siblings:closed,
    QTreeView::branch:closed:has-children:has-siblings {{
        image: none;
        border-image: none;
    }}
    QTreeView::branch:open:has-children:!has-siblings,
    QTreeView::branch:open:has-children:has-siblings {{
        image: none;
        border-image: none;
    }}
    """

def _estilo_labels(p):
    return f"""
    QLabel {{
        color: {p['texto_principal']};
        padding: 4px;
        font-size: 13px;
    }}
    """

def _estilo_splitter(p):
    return f"""
    QSplitter::handle {{
        background-color: {p['borde']};
        margin: 0px 2px;
        width: 2px;
    }}
    QSplitter::handle:hover {{
        background-color: {p['acento']};
    }}
    """

def _estilo_status_bar(p):
    return f"""
    QWidget#status_bar_container {{
        background-color: {p['fondo_secundario']};
        border-top: 1px solid {p['borde']};
        padding: 6px 12px;
    }}
    """

def _estilo_scrollbars(p):
    return f"""
    QScrollBar:vertical {{
        background: {p['fondo_principal']};
        width: 10px;
        margin: 0px;
        border-radius: 5px;
    }}
    QScrollBar::handle:vertical {{
        background: {p['fondo_terciario']};
        min-height: 30px;
        border-radius: 5px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {p['acento']};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar:horizontal {{
        background: {p['fondo_principal']};
        height: 10px;
        border-radius: 5px;
    }}
    QScrollBar::handle:horizontal {{
        background: {p['fondo_terciario']};
        min-width: 30px;
        border-radius: 5px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {p['acento']};
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}
    """