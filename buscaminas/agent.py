"""
Agentes para resolución de Buscaminas:
- AgenteQLearningAproximado (RL con aproximación lineal)
- AgenteAleatorio (Línea base aleatoria)
- AgenteHeuristico (Solucionador CSP por deducción lógica)
"""

from __future__ import annotations

import json
import pickle
import random
from pathlib import Path
from typing import List, Tuple, Sequence, Optional, Union, Dict, Set


Action = Tuple[int, int]
BoardState = Sequence[Sequence[int]]


class AgenteQLearningAproximado:
    """
    Agente de Aprendizaje por Refuerzo mediante Q-Learning con Aproximación Lineal.
    Evalúa cada acción candidata mediante un vector de características locales.
    """

    FEATURE_NAMES = [
        "bias",
        "vecinos_ocultos",
        "vecinos_bandera",
        "tiene_pista_cerca",
        "suma_pistas",
        "vecino_satisfecho",
    ]

    def __init__(
        self,
        actions: Sequence[Action],
        epsilon: float = 0.9,
        alpha: float = 0.01,
        gamma: float = 0.9,
        weights: Optional[List[float]] = None,
        rng: Optional[random.Random] = None,
    ) -> None:
        self.actions: List[Action] = list(actions)
        self.epsilon: float = float(epsilon)
        self.alpha: float = float(alpha)
        self.gamma: float = float(gamma)
        self.rng: random.Random = rng if rng is not None else random.Random()
        self.weights: List[float] = list(weights) if weights is not None else [0.0] * 6

    def get_features(self, state: BoardState, x: int, y: int) -> List[float]:
        """
        Extrae características locales de la celda (x, y) dado el estado del tablero.
        state[i][j]: -1 (oculto), -2 (bandera), >= 0 (número revelado).
        """
        rows = len(state)
        cols = len(state[0])

        vecinos_coords = [
            (nx, ny)
            for nx in range(max(0, x - 1), min(rows, x + 2))
            for ny in range(max(0, y - 1), min(cols, y + 2))
            if (nx, ny) != (x, y)
        ]

        n_ocultos = 0
        n_banderas = 0
        suma_pistas = 0
        es_vecino_satisfecho = 0.0

        for nx, ny in vecinos_coords:
            val = state[nx][ny]
            if val == -1:
                n_ocultos += 1
            elif val == -2:
                n_banderas += 1
            elif val >= 0:
                suma_pistas += val

                # Lógica de vecino satisfecho:
                # Si una celda numérica vecina N ya tiene N banderas alrededor,
                # sus celdas ocultas restantes son seguras.
                banderas_vecino = sum(
                    1
                    for vx in range(max(0, nx - 1), min(rows, nx + 2))
                    for vy in range(max(0, ny - 1), min(cols, ny + 2))
                    if (vx, vy) != (nx, ny) and state[vx][vy] == -2
                )
                if banderas_vecino == val:
                    es_vecino_satisfecho = 1.0

        return [
            1.0,
            float(n_ocultos * 0.1),
            float(n_banderas * 0.5),
            1.0 if suma_pistas > 0 else 0.0,
            float(suma_pistas * 0.1),
            float(es_vecino_satisfecho * 2.0),
        ]

    def get_q_value(self, state: BoardState, action: Action) -> float:
        """Calcula el valor Q: Q(s, a) = w . f(s, a)."""
        x, y = action
        features = self.get_features(state, x, y)
        return sum(w * f for w, f in zip(self.weights, features))

    def get_acciones_validas(self, state: BoardState) -> List[Action]:
        """Filtra únicamente las celdas ocultas (-1)."""
        return [(x, y) for (x, y) in self.actions if state[x][y] == -1]

    def elegir_accion(self, state: BoardState) -> Action:
        """Selecciona una acción siguiendo la política epsilon-greedy."""
        acciones_validas = self.get_acciones_validas(state)
        if not acciones_validas:
            return self.rng.choice(self.actions)

        if self.rng.random() < self.epsilon:
            return self.rng.choice(acciones_validas)

        best_q = -float("inf")
        best_actions: List[Action] = []

        for accion in acciones_validas:
            q = self.get_q_value(state, accion)
            if q > best_q:
                best_q = q
                best_actions = [accion]
            elif abs(q - best_q) < 1e-9:
                best_actions.append(accion)

        return self.rng.choice(best_actions)

    def aprender(
        self,
        state: BoardState,
        action: Action,
        reward: float,
        next_state: BoardState,
    ) -> float:
        """
        Actualiza los pesos usando descenso de gradiente TD(0):
        w = w + alpha * (reward + gamma * max_a' Q(s', a') - Q(s, a)) * f(s, a).
        Retorna el error TD.
        """
        x, y = action
        current_q = self.get_q_value(state, action)
        features = self.get_features(state, x, y)

        acciones_futuras = self.get_acciones_validas(next_state)
        max_next_q = 0.0
        if acciones_futuras:
            max_next_q = max(self.get_q_value(next_state, a) for a in acciones_futuras)

        td_target = reward + (self.gamma * max_next_q)
        td_error = td_target - current_q

        for i in range(len(self.weights)):
            self.weights[i] += self.alpha * td_error * features[i]

        return td_error

    def guardar_agente(self, filename: Union[str, Path] = "mi_agente_entrenado.pkl") -> None:
        """Guarda los pesos del agente en formato pickle."""
        path = Path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self.weights, f)

    def cargar_agente(self, filename: Union[str, Path] = "mi_agente_entrenado.pkl") -> bool:
        """Carga los pesos del agente desde pickle."""
        path = Path(filename)
        if not path.is_file():
            return False
        with open(path, "rb") as f:
            self.weights = list(pickle.load(f))
        return True

    def guardar_json(self, filename: Union[str, Path]) -> None:
        """Guarda los pesos y metadatos en formato JSON legible."""
        path = Path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "version": "2.0",
            "feature_names": self.FEATURE_NAMES,
            "weights": self.weights,
            "epsilon": self.epsilon,
            "alpha": self.alpha,
            "gamma": self.gamma,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def cargar_json(self, filename: Union[str, Path]) -> bool:
        """Carga los pesos desde formato JSON."""
        path = Path(filename)
        if not path.is_file():
            return False
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.weights = list(data["weights"])
        return True


class AgenteAleatorio:
    """Agente que selecciona uniformemente una celda oculta válida."""

    def __init__(self, acciones_posibles: Sequence[Action], rng: Optional[random.Random] = None) -> None:
        self.acciones: List[Action] = list(acciones_posibles)
        self.rng: random.Random = rng if rng is not None else random.Random()

    def elegir_accion(self, state: BoardState) -> Action:
        validas = [(x, y) for (x, y) in self.acciones if state[x][y] == -1]
        if not validas:
            return self.rng.choice(self.acciones)
        return self.rng.choice(validas)


class AgenteHeuristico:
    """
    Agente resolutor basado en satisfacción de restricciones (CSP).
    Aplica deducción lógica determinista:
    1. Si una celda con número N ya tiene N banderas alrededor, todos sus vecinos ocultos son 100% seguros.
    2. Si no hay celdas trivialmente seguras, analiza restricciones de subconjuntos.
    3. Si debe adivinar, elige la celda oculta con menor probabilidad heurística de mina.
    """

    def __init__(self, acciones_posibles: Sequence[Action], rng: Optional[random.Random] = None) -> None:
        self.acciones: List[Action] = list(acciones_posibles)
        self.rng: random.Random = rng if rng is not None else random.Random()

    def elegir_accion(self, state: BoardState) -> Action:
        rows = len(state)
        cols = len(state[0])

        ocultas_validas = [(x, y) for (x, y) in self.acciones if state[x][y] == -1]
        if not ocultas_validas:
            return self.rng.choice(self.acciones)

        # Regla 1: Deducción directa de vecinos seguros (vecinos satisfechos)
        seguros: Set[Action] = set()
        for x in range(rows):
            for y in range(cols):
                val = state[x][y]
                if val >= 0:
                    vecinos = [
                        (nx, ny)
                        for nx in range(max(0, x - 1), min(rows, x + 2))
                        for ny in range(max(0, y - 1), min(cols, y + 2))
                        if (nx, ny) != (x, y)
                    ]
                    banderas = sum(1 for (nx, ny) in vecinos if state[nx][ny] == -2)
                    ocultos = [(nx, ny) for (nx, ny) in vecinos if state[nx][ny] == -1]

                    if banderas == val and ocultos:
                        seguros.update(ocultos)

        if seguros:
            return sorted(list(seguros))[0]

        # Regla 2: Restricciones de subconjuntos entre pares de celdas
        # Para cada número, la ecuación es sum(ocultos) = val - banderas.
        ecuaciones: List[Tuple[Set[Action], int]] = []
        for x in range(rows):
            for y in range(cols):
                val = state[x][y]
                if val >= 0:
                    vecinos = [
                        (nx, ny)
                        for nx in range(max(0, x - 1), min(rows, x + 2))
                        for ny in range(max(0, y - 1), min(cols, y + 2))
                        if (nx, ny) != (x, y)
                    ]
                    banderas = sum(1 for (nx, ny) in vecinos if state[nx][ny] == -2)
                    ocultos = {(nx, ny) for (nx, ny) in vecinos if state[nx][ny] == -1}
                    restantes = val - banderas
                    if ocultos:
                        ecuaciones.append((ocultos, restantes))

        # Comparar pares de restricciones (A subset B)
        for i, (set_a, val_a) in enumerate(ecuaciones):
            for j, (set_b, val_b) in enumerate(ecuaciones):
                if i != j and set_a.issubset(set_b) and len(set_a) < len(set_b):
                    diff_set = set_b - set_a
                    diff_val = val_b - val_a
                    if diff_val == 0:
                        # Todo lo en diff_set es seguro
                        return sorted(list(diff_set))[0]

        # Regla 3: Si no hay certeza absoluta, minimizar el riesgo estimado
        # Estimar probabilidad como proporción local de minas requeridas
        riesgo: Dict[Action, float] = {act: 0.5 for act in ocultas_validas}
        for s, v in ecuaciones:
            prob = max(0.0, min(1.0, v / len(s)))
            for act in s:
                riesgo[act] = max(riesgo[act], prob)

        mejor_accion = min(ocultas_validas, key=lambda a: (riesgo.get(a, 0.5), self.rng.random()))
        return mejor_accion
