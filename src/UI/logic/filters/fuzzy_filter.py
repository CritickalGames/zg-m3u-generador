from rapidfuzz import fuzz

class FiltroFuzzyProxyModel:
    def __init__(self, vista, modelo):
        self._vista = vista
        self._modelo = modelo
        self._texto = ""
        self._umbral = 60

    def aplicar_filtro(self, texto):
        self._texto = texto.lower().strip()
        self._refrescar_visibilidad(self._modelo.invisibleRootItem())

    def _refrescar_visibilidad(self, nodo):
        for i in range(nodo.rowCount()):
            hijo = nodo.child(i)
            _actualizar_visibilidad_hijo(hijo, self._texto, self._umbral)
            self._refrescar_visibilidad(hijo)

def _actualizar_visibilidad_hijo(hijo, texto, umbral):
    if not texto:
        hijo._es_visible = True
    else:
        nombre = hijo.text().lower()
        puntaje = fuzz.partial_ratio(texto, nombre)
        hijo._es_visible = puntaje >= umbral or _tiene_descendiente_visible(hijo, texto, umbral)

def _tiene_descendiente_visible(nodo, texto, umbral):
    for i in range(nodo.rowCount()):
        hijo = nodo.child(i)
        nombre = hijo.text().lower()
        if fuzz.partial_ratio(texto, nombre) >= umbral:
            return True
        if _tiene_descendiente_visible(hijo, texto, umbral):
            return True
    return False