# coding=utf-8
# Python 3
# File: juego_model.py

import random
from collections import deque

# --- Constantes de Estado ---
STATE_DEFAULT = 0
STATE_CLICKED = 1
STATE_FLAGGED = 2

class Celda:
    """
    Representa el estado lógico de una celda, sin interfaz gráfica.
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.id = f"{x}_{y}"
        self.es_mina = False
        self.estado = STATE_DEFAULT
        self.minas_vecinas = 0

class Tablero:
    """
    Representa el tablero y maneja toda la lógica del juego.
    No sabe nada sobre tkinter.
    """
    def __init__(self, size_x, size_y, mine_ratio=0.1):
        self.size_x = size_x
        self.size_y = size_y
        self.mine_ratio = mine_ratio

        self.celdas = {}  # Usamos un diccionario de diccionarios
        self.minas_totales = 0
        self.conteo_banderas = 0
        self.conteo_reveladas = 0
        self.juego_terminado = False
        self.victoria = False

        self.reiniciar() # Inicializa el tablero

    def reiniciar(self):
        """Reinicia el estado del tablero para un nuevo juego."""
        self.celdas = {}
        self.minas_totales = 0
        self.conteo_banderas = 0
        self.conteo_reveladas = 0
        self.juego_terminado = False
        self.victoria = False

        self._crear_grid()
        self._calcular_vecinos()

    def _crear_grid(self):
        """Llena el tablero con Celdas y coloca las minas."""
        for x in range(0, self.size_x):
            self.celdas[x] = {}
            for y in range(0, self.size_y):
                celda = Celda(x, y)

                # Colocar minas aleatoriamente
                if random.uniform(0.0, 1.0) < self.mine_ratio:
                    celda.es_mina = True
                    self.minas_totales += 1

                self.celdas[x][y] = celda

    def _calcular_vecinos(self):
        """Calcula el número de minas adyacentes para cada celda."""
        for x in range(0, self.size_x):
            for y in range(0, self.size_y):
                if self.celdas[x][y].es_mina:
                    continue

                conteo_minas = 0
                for vecino in self.get_vecinos(x, y):
                    if vecino.es_mina:
                        conteo_minas += 1
                self.celdas[x][y].minas_vecinas = conteo_minas

    def get_vecinos(self, x, y):
        """Devuelve una lista de Celdas vecinas válidas."""
        vecinos = []
        coords = [
            {"x": x-1, "y": y-1},  # top left
            {"x": x-1, "y": y},    # top middle
            {"x": x-1, "y": y+1},  # top right
            {"x": x,   "y": y-1},  # left
            {"x": x,   "y": y+1},  # right
            {"x": x+1, "y": y-1},  # bottom left
            {"x": x+1, "y": y},    # bottom middle
            {"x": x+1, "y": y+1},  # bottom right
        ]
        for n in coords:
            try:
                # Verificar que la coordenada existe en el diccionario
                vecinos.append(self.celdas[n["x"]][n["y"]])
            except KeyError:
                pass  # Ocurre si la coordenada está fuera del tablero
        return vecinos

    def marcar_celda(self, x, y):
        """
        Alterna la bandera en una celda.
        Devuelve la celda modificada.
        """
        celda = self.celdas[x][y]
        if self.juego_terminado or celda.estado == STATE_CLICKED:
            return None # No se puede marcar una celda revelada

        if celda.estado == STATE_DEFAULT:
            celda.estado = STATE_FLAGGED
            self.conteo_banderas += 1
        elif celda.estado == STATE_FLAGGED:
            celda.estado = STATE_DEFAULT
            self.conteo_banderas -= 1

        return celda

    def revelar_celda(self, x, y):
        """
        Revela una celda. Si es un 0, propaga la revelación.
        Devuelve una lista de todas las celdas que fueron reveladas.
        """
        celda_inicial = self.celdas[x][y]

        # No revelar si está marcada o ya revelada
        if celda_inicial.estado != STATE_DEFAULT:
            return []

        celdas_actualizadas = []
        queue = deque([celda_inicial])

        while len(queue) != 0:
            celda = queue.popleft()

            # Solo procesar si no ha sido ya revelada (en este mismo clic)
            if celda.estado == STATE_DEFAULT:
                celda.estado = STATE_CLICKED
                self.conteo_reveladas += 1
                celdas_actualizadas.append(celda)

                # Si la celda es un 0, agregar vecinos a la cola
                if celda.minas_vecinas == 0:
                    for v in self.get_vecinos(celda.x, celda.y):
                        if v.estado == STATE_DEFAULT:
                            queue.append(v)

        self._chequear_victoria()
        return celdas_actualizadas

    def _chequear_victoria(self):
        """Verifica si el juego ha sido ganado."""
        celdas_seguras_totales = (self.size_x * self.size_y) - self.minas_totales
        if self.conteo_reveladas == celdas_seguras_totales:
            self.juego_terminado = True
            self.victoria = True

    def get_celda(self, x, y):
        """Obtiene una celda por coordenadas."""
        try:
            return self.celdas[x][y]
        except KeyError:
            return None