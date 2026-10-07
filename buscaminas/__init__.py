"""
Buscaminas (Minesweeper) package with Reinforcement Learning and Heuristic Solvers.
"""

from buscaminas.model import Tablero, Celda, STATE_DEFAULT, STATE_CLICKED, STATE_FLAGGED, REWARDS
from buscaminas.agent import AgenteQLearningAproximado, AgenteAleatorio, AgenteHeuristico
from buscaminas.gui import MinesweeperGUI, AgenteGUI

__all__ = [
    "Tablero",
    "Celda",
    "STATE_DEFAULT",
    "STATE_CLICKED",
    "STATE_FLAGGED",
    "REWARDS",
    "AgenteQLearningAproximado",
    "AgenteAleatorio",
    "AgenteHeuristico",
    "MinesweeperGUI",
    "AgenteGUI",
]

__version__ = "2.0.0"
