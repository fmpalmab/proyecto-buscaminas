"""
Modelo lógico del juego Buscaminas.
Implementa las reglas, estados, flood-fill, auto-flagging y el entorno compatible con RL.
"""

from __future__ import annotations

import random
from collections import deque
from typing import Dict, List, Optional, Tuple, Set

# --- Constantes de Estado ---
STATE_DEFAULT: int = 0
STATE_CLICKED: int = 1
STATE_FLAGGED: int = 2

# --- Recompensas para el Agente (Q-Learning) ---
REWARDS: Dict[str, float] = {
    "win": 100.0,
    "lose": -100.0,
    "progress": 1.0,
    "guess": -0.5,
    "no_progress": -1.0,
}


class Celda:
    """Representa el estado lógico de una celda individual."""

    def __init__(self, x: int, y: int) -> None:
        self.x: int = x
        self.y: int = y
        self.id: str = f"{x}_{y}"
        self.es_mina: bool = False
        self.estado: int = STATE_DEFAULT
        self.minas_vecinas: int = 0

    def __repr__(self) -> str:
        return f"Celda(x={self.x}, y={self.y}, mina={self.es_mina}, estado={self.estado}, pistas={self.minas_vecinas})"


class Tablero:
    """
    Representa el tablero y maneja toda la lógica del juego.
    Incluye adaptaciones para interacción humana y entornos de RL.
    """

    def __init__(self, size_x: int, size_y: int, mine_ratio: float = 0.1, rng: Optional[random.Random] = None) -> None:
        self.size_x: int = size_x
        self.size_y: int = size_y
        self.mine_ratio: float = mine_ratio
        self.rng: random.Random = rng if rng is not None else random.Random()

        self.celdas: Dict[int, Dict[int, Celda]] = {}
        self.minas_totales: int = 0
        self.conteo_banderas: int = 0
        self.conteo_reveladas: int = 0

        self.juego_terminado: bool = False
        self.victoria: bool = False
        self.primer_movimiento: bool = True

        self.reiniciar()

    def reiniciar(self) -> None:
        """Reinicia el estado del tablero para un nuevo juego."""
        self.celdas = {}
        self.minas_totales = 0
        self.conteo_banderas = 0
        self.conteo_reveladas = 0
        self.juego_terminado = False
        self.victoria = False
        self.primer_movimiento = True

        self._crear_grid_vacio()

    def _crear_grid_vacio(self) -> None:
        """Inicializa las celdas vacías sin minas."""
        for x in range(self.size_x):
            self.celdas[x] = {}
            for y in range(self.size_y):
                self.celdas[x][y] = Celda(x, y)

    def _generar_minas_seguras(self, safe_x: int, safe_y: int) -> None:
        """
        Coloca las minas aleatoriamente garantizando que (safe_x, safe_y)
        esté libre de minas.
        """
        celdas_posibles: List[Celda] = []
        for x in range(self.size_x):
            for y in range(self.size_y):
                if x != safe_x or y != safe_y:
                    celdas_posibles.append(self.celdas[x][y])

        total_disponibles = len(celdas_posibles)
        n_minas = int(total_disponibles * self.mine_ratio)
        if n_minas == 0 and self.mine_ratio > 0 and total_disponibles > 0:
            n_minas = 1

        n_minas = min(n_minas, total_disponibles)
        minas_elegidas = self.rng.sample(celdas_posibles, n_minas)

        for celda in minas_elegidas:
            celda.es_mina = True
            self.minas_totales += 1

        self._calcular_vecinos()

    def _calcular_vecinos(self) -> None:
        """Calcula el número de minas adyacentes para cada celda no-mina."""
        for x in range(self.size_x):
            for y in range(self.size_y):
                celda = self.celdas[x][y]
                celda.minas_vecinas = 0

                if celda.es_mina:
                    continue

                conteo = 0
                for vecino in self.get_vecinos(x, y):
                    if vecino.es_mina:
                        conteo += 1
                celda.minas_vecinas = conteo

    def get_vecinos(self, x: int, y: int) -> List[Celda]:
        """Devuelve una lista de celdas vecinas válidas en 8 direcciones."""
        vecinos: List[Celda] = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.size_x and 0 <= ny < self.size_y:
                    vecinos.append(self.celdas[nx][ny])
        return vecinos

    def marcar_celda(self, x: int, y: int) -> Optional[Celda]:
        """Alterna la bandera en una celda no revelada."""
        celda = self.get_celda(x, y)
        if celda is None or self.juego_terminado or celda.estado == STATE_CLICKED:
            return None

        if celda.estado == STATE_DEFAULT:
            celda.estado = STATE_FLAGGED
            self.conteo_banderas += 1
        elif celda.estado == STATE_FLAGGED:
            celda.estado = STATE_DEFAULT
            self.conteo_banderas -= 1

        return celda

    def revelar_celda(self, x: int, y: int) -> List[Celda]:
        """
        Revela una celda. Si el valor es 0, propaga la revelación mediante flood-fill (BFS).
        """
        celda_inicial = self.get_celda(x, y)
        if celda_inicial is None or celda_inicial.estado != STATE_DEFAULT:
            return []

        if self.primer_movimiento:
            self._generar_minas_seguras(x, y)
            self.primer_movimiento = False
            if celda_inicial.es_mina:
                return []

        celdas_actualizadas: List[Celda] = []
        queue: deque[Celda] = deque([celda_inicial])

        while queue:
            celda = queue.popleft()
            if celda.estado == STATE_DEFAULT:
                celda.estado = STATE_CLICKED
                self.conteo_reveladas += 1
                celdas_actualizadas.append(celda)

                if celda.minas_vecinas == 0 and not celda.es_mina:
                    for v in self.get_vecinos(celda.x, celda.y):
                        if v.estado == STATE_DEFAULT:
                            queue.append(v)

        self._chequear_victoria()
        return celdas_actualizadas

    def _chequear_victoria(self) -> None:
        """Verifica si todas las celdas seguras han sido reveladas."""
        celdas_seguras_totales = (self.size_x * self.size_y) - self.minas_totales
        if self.minas_totales > 0 and self.conteo_reveladas == celdas_seguras_totales:
            self.juego_terminado = True
            self.victoria = True

    def get_celda(self, x: int, y: int) -> Optional[Celda]:
        """Devuelve una celda por coordenadas o None si está fuera de rango."""
        if 0 <= x < self.size_x and 0 <= y < self.size_y:
            return self.celdas[x][y]
        return None

    def get_estado_hashable(self) -> Tuple[Tuple[int, ...], ...]:
        """
        Genera representación inmutable del tablero visible:
        -1: Oculto (DEFAULT)
        -2: Bandera (FLAGGED)
        0-8: Número de minas vecinas (CLICKED)
        """
        estado: List[Tuple[int, ...]] = []
        for x in range(self.size_x):
            fila: List[int] = []
            for y in range(self.size_y):
                celda = self.celdas[x][y]
                if celda.estado == STATE_DEFAULT:
                    fila.append(-1)
                elif celda.estado == STATE_FLAGGED:
                    fila.append(-2)
                else:
                    fila.append(celda.minas_vecinas)
            estado.append(tuple(fila))
        return tuple(estado)

    def _auto_flag(self) -> int:
        """
        Detecta minas obvias y coloca banderas automáticamente.
        Regla: si una celda revelada N tiene exactamente N vecinos no revelados
        (ocultos + banderas), todos los vecinos ocultos deben ser banderas.
        Retorna la cantidad de banderas nuevas colocadas.
        """
        total_nuevas = 0
        cambios = True
        while cambios:
            cambios = False
            for x in range(self.size_x):
                for y in range(self.size_y):
                    celda = self.celdas[x][y]
                    if celda.estado == STATE_CLICKED and not celda.es_mina:
                        vecinos = self.get_vecinos(x, y)
                        ocultos = [v for v in vecinos if v.estado == STATE_DEFAULT]
                        banderas = [v for v in vecinos if v.estado == STATE_FLAGGED]
                        total_indeterminados = len(ocultos) + len(banderas)

                        if celda.minas_vecinas == total_indeterminados and ocultos:
                            for v in ocultos:
                                v.estado = STATE_FLAGGED
                                self.conteo_banderas += 1
                                total_nuevas += 1
                                cambios = True
        return total_nuevas

    def step(self, x: int, y: int) -> Tuple[Tuple[Tuple[int, ...], ...], float, bool]:
        """
        Ejecuta un paso de interacción (revelar celda) en el entorno.
        Retorna (next_state, reward, done).
        """
        celda = self.get_celda(x, y)

        if celda is None or celda.estado == STATE_CLICKED or celda.estado == STATE_FLAGGED:
            return self.get_estado_hashable(), REWARDS["no_progress"], self.juego_terminado

        if self.primer_movimiento:
            self._generar_minas_seguras(x, y)
            self.primer_movimiento = False

        if celda.es_mina:
            self.juego_terminado = True
            self.victoria = False
            celda.estado = STATE_CLICKED
            return self.get_estado_hashable(), REWARDS["lose"], True

        reveladas_antes = self.conteo_reveladas

        tiene_pista_cerca = any(v.estado == STATE_CLICKED and not v.es_mina for v in self.get_vecinos(x, y))

        self.revelar_celda(x, y)
        self._auto_flag()

        done = self.juego_terminado
        if self.victoria:
            reward = REWARDS["win"]
        elif done:
            reward = REWARDS["lose"]
        else:
            if self.conteo_reveladas > reveladas_antes:
                if not tiene_pista_cerca:
                    reward = REWARDS["guess"]
                else:
                    diff = self.conteo_reveladas - reveladas_antes
                    reward = REWARDS["progress"] * (1.0 + (diff * 0.1))
            else:
                reward = REWARDS["no_progress"]

        return self.get_estado_hashable(), reward, done

    def to_ascii(self) -> str:
        """Devuelve una representación en texto del tablero visible para modo terminal."""
        lines: List[str] = ["  " + " ".join(f"{c:2d}" for c in range(self.size_y))]
        for r in range(self.size_x):
            row_symbols: List[str] = []
            for c in range(self.size_y):
                cell = self.celdas[r][c]
                if cell.estado == STATE_DEFAULT:
                    row_symbols.append(" .")
                elif cell.estado == STATE_FLAGGED:
                    row_symbols.append(" F")
                elif cell.es_mina:
                    row_symbols.append(" *")
                elif cell.minas_vecinas == 0:
                    row_symbols.append("  ")
                else:
                    row_symbols.append(f" {cell.minas_vecinas}")
            lines.append(f"{r:2d}" + "".join(row_symbols))
        return "\n".join(lines)
