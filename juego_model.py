# coding=utf-8
# Python 3
# File: juego_model.py

import random
from collections import deque

# --- Constantes de Estado ---
STATE_DEFAULT = 0
STATE_CLICKED = 1
STATE_FLAGGED = 2

# --- Recompensas para el Agente (Q-Learning) ---
REWARDS = {
    'win': 100,         # Victoria
    'lose': -100,       # Derrota (Mina)
    'progress': 1,      # Revelar celda segura (base)
    'guess': -0.5,      # Castigo leve por adivinar (opcional)
    'no_progress': -1   # Castigo por intentar revelar una ya revelada
}

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
    Incluye adaptaciones para entrenamiento de Agentes IA.
    """
    def __init__(self, size_x, size_y, mine_ratio=0.1):
        self.size_x = size_x
        self.size_y = size_y
        self.mine_ratio = mine_ratio

        self.celdas = {}
        self.minas_totales = 0
        self.conteo_banderas = 0
        self.conteo_reveladas = 0
        
        # Banderas de estado del juego
        self.juego_terminado = False
        self.victoria = False
        self.primer_movimiento = True  # Para lógica de primer clic seguro

        self.reiniciar() 

    def reiniciar(self):
        """Reinicia el estado del tablero para un nuevo juego."""
        self.celdas = {}
        self.minas_totales = 0
        self.conteo_banderas = 0
        self.conteo_reveladas = 0
        self.juego_terminado = False
        self.victoria = False
        self.primer_movimiento = True

        self._crear_grid_vacio()

    def _crear_grid_vacio(self):
        """Inicializa las celdas vacías, SIN minas todavía."""
        for x in range(self.size_x):
            self.celdas[x] = {}
            for y in range(self.size_y):
                self.celdas[x][y] = Celda(x, y)

    def _generar_minas_seguras(self, safe_x, safe_y):
        """
        Coloca las minas aleatoriamente PERO garantiza que la coordenada
        (safe_x, safe_y) no tenga mina. Se llama en el primer clic.
        """
        celdas_posibles = []
        for x in range(self.size_x):
            for y in range(self.size_y):
                # Excluir la celda del primer clic
                if x != safe_x or y != safe_y:
                    celdas_posibles.append(self.celdas[x][y])

        # Calcular cuántas minas poner
        n_minas = int(len(celdas_posibles) * self.mine_ratio)
        if n_minas == 0 and self.mine_ratio > 0:
            n_minas = 1  # Asegurar al menos 1 mina

        minas_elegidas = random.sample(celdas_posibles, n_minas)
        
        for celda in minas_elegidas:
            celda.es_mina = True
            self.minas_totales += 1
            
        # Una vez puestas las minas, calculamos los números
        self._calcular_vecinos()

    def _calcular_vecinos(self):
        """Calcula el número de minas adyacentes para cada celda."""
        for x in range(self.size_x):
            for y in range(self.size_y):
                self.celdas[x][y].minas_vecinas = 0 # Resetear
                
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
            {"x": x-1, "y": y-1}, {"x": x-1, "y": y}, {"x": x-1, "y": y+1},
            {"x": x,   "y": y-1},                     {"x": x,   "y": y+1},
            {"x": x+1, "y": y-1}, {"x": x+1, "y": y}, {"x": x+1, "y": y+1},
        ]
        for n in coords:
            try:
                vecinos.append(self.celdas[n["x"]][n["y"]])
            except KeyError:
                pass 
        return vecinos

    def marcar_celda(self, x, y):
        """Alterna la bandera en una celda."""
        celda = self.celdas[x][y]
        if self.juego_terminado or celda.estado == STATE_CLICKED:
            return None 

        if celda.estado == STATE_DEFAULT:
            celda.estado = STATE_FLAGGED
            self.conteo_banderas += 1
        elif celda.estado == STATE_FLAGGED:
            celda.estado = STATE_DEFAULT
            self.conteo_banderas -= 1

        return celda

    def revelar_celda(self, x, y):
        """
        Revela una celda. Si es un 0, propaga la revelación (flood fill).
        NOTA: Este método asume que YA se chequearon minas o primer movimiento
        antes de llamarlo (ver método step o onClick en GUI).
        """
        celda_inicial = self.celdas[x][y]

        if celda_inicial.estado != STATE_DEFAULT:
            return []

        # Si es el primer movimiento desde la GUI (no desde el agente), 
        # necesitamos generar las minas aquí también para que el humano no explote.
        if self.primer_movimiento:
            self._generar_minas_seguras(x, y)
            self.primer_movimiento = False
            # Si justo era mina (imposible por la lógica anterior, pero por seguridad):
            if celda_inicial.es_mina:
                return []

        celdas_actualizadas = []
        queue = deque([celda_inicial])

        while len(queue) != 0:
            celda = queue.popleft()

            if celda.estado == STATE_DEFAULT:
                celda.estado = STATE_CLICKED
                self.conteo_reveladas += 1
                celdas_actualizadas.append(celda)

                if celda.minas_vecinas == 0:
                    for v in self.get_vecinos(celda.x, celda.y):
                        if v.estado == STATE_DEFAULT:
                            queue.append(v)

        self._chequear_victoria()
        return celdas_actualizadas

    def _chequear_victoria(self):
        """Verifica si el juego ha sido ganado."""
        celdas_seguras_totales = (self.size_x * self.size_y) - self.minas_totales
        # Verificar que se hayan generado minas (minas_totales > 0) para evitar ganar al inicio
        if self.minas_totales > 0 and self.conteo_reveladas == celdas_seguras_totales:
            self.juego_terminado = True
            self.victoria = True

    def get_celda(self, x, y):
        """Obtiene una celda por coordenadas."""
        try:
            return self.celdas[x][y]
        except KeyError:
            return None

    # --- MÉTODOS PARA EL AGENTE (IA) ---

    def get_estado_hashable(self):
        """
        Genera una representación inmutable del tablero para usar como clave en Q-Learning.
        -1: Oculto/Bandera
        0-8: Revelado (número)
        """
        estado = []
        for x in range(self.size_x):
            fila = []
            for y in range(self.size_y):
                celda = self.celdas[x][y]
                if celda.estado == STATE_DEFAULT or celda.estado == STATE_FLAGGED:
                    fila.append(-1)
                else:
                    fila.append(celda.minas_vecinas)
            estado.append(tuple(fila))
        return tuple(estado)

    def step(self, x, y):
        """
        Ejecuta una acción del agente y devuelve (estado, recompensa, terminado).
        Maneja internamente la lógica de 'Primer Clic Seguro' y 'Game Over'.
        """
        celda = self.get_celda(x, y)
        
        # 1. Acción Inválida
        if celda is None or celda.estado == STATE_CLICKED or celda.estado == STATE_FLAGGED:
            return self.get_estado_hashable(), REWARDS['no_progress'], self.juego_terminado

        # 2. Primer Movimiento (Generación diferida de minas)
        if self.primer_movimiento:
            self._generar_minas_seguras(x, y)
            self.primer_movimiento = False

        # 3. Verificar si pisó mina
        if celda.es_mina:
            self.juego_terminado = True
            self.victoria = False
            celda.estado = STATE_CLICKED # Mostrar la mina al agente
            return self.get_estado_hashable(), REWARDS['lose'], True

        # 4. Jugada normal (segura)
        reveladas_antes = self.conteo_reveladas
        
        # --- LÓGICA NUEVA: DETECTAR SI ES ADIVINANZA ---
        # Verificar si la celda tiene al menos un vecino revelado (pista)
        tiene_pista_cerca = False
        for v in self.get_vecinos(x, y):
            if v.estado == STATE_CLICKED: # Si hay un número cerca
                tiene_pista_cerca = True
                break
        # -----------------------------------------------

        self.revelar_celda(x, y) 

        # 5. Calcular Recompensa
        reward = 0
        done = self.juego_terminado

        if self.victoria:
            reward = REWARDS['win']
        elif done:
            reward = REWARDS['lose']
        else:
            if self.conteo_reveladas > reveladas_antes:
                if not tiene_pista_cerca:
                    # ¡CASTIGO! Reveló celda pero fue suerte (adivinanza a ciegas)
                    reward = REWARDS['guess'] # Asegúrate de que esto sea negativo (ej. -0.5)
                else:
                    # PREMIO: Jugada lógica (estaba cerca de una pista)
                    diff = self.conteo_reveladas - reveladas_antes
                    reward = REWARDS['progress'] * (1 + (diff * 0.1))
            else:
                reward = REWARDS['no_progress']

        return self.get_estado_hashable(), reward, done