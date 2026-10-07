"""
Compatibility shim for juego_model.py.
Forwards to the modernized buscaminas.model package.
"""

from buscaminas.model import (
    Celda,
    Tablero,
    STATE_DEFAULT,
    STATE_CLICKED,
    STATE_FLAGGED,
    REWARDS,
)

__all__ = [
    "Celda",
    "Tablero",
    "STATE_DEFAULT",
    "STATE_CLICKED",
    "STATE_FLAGGED",
    "REWARDS",
]