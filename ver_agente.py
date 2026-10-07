"""
Demostración visual del agente IA jugando en tiempo real.
"""

import tkinter as tk
from buscaminas.model import Tablero
from buscaminas.agent import AgenteQLearningAproximado
from buscaminas.gui import AgenteGUI

SIZE = 6
MINAS_RATIO = 0.15
VELOCIDAD = 450


def main():
    root = tk.Tk()
    root.title(f"Demo Agente Buscaminas ({SIZE}x{SIZE})")

    tablero = Tablero(SIZE, SIZE, MINAS_RATIO)
    acciones = [(x, y) for x in range(SIZE) for y in range(SIZE)]
    agente = AgenteQLearningAproximado(actions=acciones)

    cargado = agente.cargar_agente("mi_agente_entrenado.pkl")
    if not cargado:
        print("Aviso: No se encontró 'mi_agente_entrenado.pkl'. Se utilizarán pesos por defecto.")

    app = AgenteGUI(root, tablero, agente, velocidad_ms=VELOCIDAD)
    root.after(800, app.iniciar_demo)
    root.mainloop()


if __name__ == "__main__":
    main()