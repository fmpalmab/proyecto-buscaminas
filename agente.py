"""
Compatibility shim for agente.py.
Forwards to the modernized buscaminas.agent package.
"""

from buscaminas.agent import (
    AgenteQLearningAproximado,
    AgenteAleatorio,
    AgenteHeuristico,
)

__all__ = [
    "AgenteQLearningAproximado",
    "AgenteAleatorio",
    "AgenteHeuristico",
]