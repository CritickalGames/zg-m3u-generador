from PyQt6.QtGui import QKeySequence, QShortcut

def configurar_atajos(ventana, editor):
    _registrar_atajo(ventana, QKeySequence("Ctrl+Z"), editor.deshacer)
    _registrar_atajo(ventana, QKeySequence("Ctrl+Y"), editor.rehacer)
    _registrar_atajo(ventana, QKeySequence("Ctrl+X"), editor.cortar)
    _registrar_atajo(ventana, QKeySequence("Ctrl+C"), editor.copiar)
    _registrar_atajo(ventana, QKeySequence("Ctrl+V"), editor.pegar)
    _registrar_atajo(ventana, QKeySequence("Delete"), editor.eliminar)
    _registrar_atajo(ventana, QKeySequence("F2"), editor.renombrar)

def _registrar_atajo(ventana, secuencia, accion):
    atajo = QShortcut(secuencia, ventana)
    atajo.activated.connect(accion)