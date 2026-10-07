"""
Compatibility shim for interfaz_gui.py.
Forwards to the modernized buscaminas.gui package.
"""

from buscaminas.gui import (
    MinesweeperGUI,
    AgenteGUI,
    BTN_CLICK,
    BTN_FLAG,
)

__all__ = [
    "MinesweeperGUI",
    "AgenteGUI",
    "BTN_CLICK",
    "BTN_FLAG",
]