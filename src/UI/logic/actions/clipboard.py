class PortapapelesInterno:
    def __init__(self):
        self._nodos = []
        self._modo = None

    def guardar_corte(self, nodos):
        self._nodos = nodos
        self._modo = "corte"

    def guardar_copia(self, nodos):
        self._nodos = nodos
        self._modo = "copia"

    def obtener_nodos(self):
        return self._nodos

    def obtener_modo(self):
        return self._modo

    def esta_vacio(self):
        return len(self._nodos) == 0

    def limpiar(self):
        self._nodos = []
        self._modo = None