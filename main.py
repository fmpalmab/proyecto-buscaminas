# coding=utf-8
# Python 3
# File: main.py

import tkinter as tk

# Importar las clases de los otros archivos
from juego_model import Tablero
from interfaz_gui import MinesweeperGUI

# --- Configuración Principal del Juego ---
SIZE_X = 6
SIZE_Y = 6
MINE_RATIO = 0.15 # x% de las celdas serán minas

def main():
    # 1. Crear la ventana principal de Tkinter
    window = tk.Tk()
    window.title("Buscaminas (Minesweeper)")

    # 2. Crear la instancia de la lógica del juego (Modelo)
    tablero_logica = Tablero(SIZE_X, SIZE_Y, MINE_RATIO)

    # 3. Crear la instancia de la GUI (Vista/Controlador)
    #    y pasarle la ventana (root) y la lógica
    MinesweeperGUI(window, tablero_logica)

    # 4. Iniciar el bucle principal de la aplicación
    window.mainloop()

if __name__ == "__main__":
    main()