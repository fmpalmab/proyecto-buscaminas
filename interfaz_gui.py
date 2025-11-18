# coding=utf-8
# Python 3
# File: interfaz_gui.py

import tkinter as tk
from tkinter import messagebox
import platform
from datetime import datetime

# Importar la lógica del juego y constantes
from juego_model import Tablero, STATE_DEFAULT, STATE_CLICKED, STATE_FLAGGED

# --- Constantes de Botones ---
BTN_CLICK = "<Button-1>"
BTN_FLAG = "<Button-2>" if platform.system() == 'Darwin' else "<Button-3>"

class MinesweeperGUI:
    """
    Maneja toda la interfaz de usuario (Tkinter) y los eventos.
    Se comunica con un objeto Tablero para la lógica.
    """
    def __init__(self, root, tablero):
        self.root = root
        self.tablero = tablero  # Referencia al modelo lógico

        # Cargar imágenes (requiere la carpeta 'images')
        try:
            self.images = {
                "plain": tk.PhotoImage(file="images/tile_plain.gif"),
                "clicked": tk.PhotoImage(file="images/tile_clicked.gif"),
                "mine": tk.PhotoImage(file="images/tile_mine.gif"),
                "flag": tk.PhotoImage(file="images/tile_flag.gif"),
                "wrong": tk.PhotoImage(file="images/tile_wrong.gif"),
                "numbers": []
            }
            for i in range(1, 9):
                self.images["numbers"].append(tk.PhotoImage(file=f"images/tile_{i}.gif"))
        except tk.TclError as e:
            print(f"Error cargando imágenes: {e}")
            print("Asegúrate de que la carpeta 'images' exista y contenga los archivos .gif")
            self.root.quit()
            return

        # Configurar el frame principal
        self.frame = tk.Frame(self.root)
        self.frame.pack()

        # UI: Etiquetas
        self.labels = {
            "time": tk.Label(self.frame, text="00:00:00"),
            "mines": tk.Label(self.frame, text="Mines: 0"),
            "flags": tk.Label(self.frame, text="Flags: 0")
        }
        self.labels["time"].grid(row=0, column=0, columnspan=self.tablero.size_y)
        # Usar división entera (//) para Py3
        self.labels["mines"].grid(row=self.tablero.size_x + 1, column=0, columnspan=self.tablero.size_y // 2)
        self.labels["flags"].grid(row=self.tablero.size_x + 1, column=self.tablero.size_y // 2, columnspan=self.tablero.size_y // 2)

        # UI: Botones (Celdas)
        self.botones = {} # Diccionario para guardar los widgets Button
        self.startTime = None

        self.setup_ui_botones()
        self.refreshLabels()
        self.updateTimer()

    def setup_ui_botones(self):
        """Crea la grilla de botones de Tkinter."""
        for x in range(0, self.tablero.size_x):
            self.botones[x] = {}
            for y in range(0, self.tablero.size_y):
                gfx = self.images["plain"]
                boton = tk.Button(self.frame, image=gfx)
                
                # Usar lambdas para pasar las coordenadas correctas al hacer clic
                boton.bind(BTN_CLICK, self.onClickWrapper(x, y))
                boton.bind(BTN_FLAG, self.onRightClickWrapper(x, y))
                boton.grid(row=x + 1, column=y) # +1 por la fila del timer
                
                self.botones[x][y] = boton

    def restart(self):
        """Reinicia el juego y la interfaz."""
        self.tablero.reiniciar()
        self.startTime = None
        for x in range(0, self.tablero.size_x):
            for y in range(0, self.tablero.size_y):
                boton = self.botones[x][y]
                boton.config(image=self.images["plain"])
                boton.bind(BTN_CLICK, self.onClickWrapper(x, y))
        self.refreshLabels()

    def refreshLabels(self):
        """Actualiza las etiquetas con datos del modelo (usando f-strings)."""
        self.labels["flags"].config(text=f"Flags: {self.tablero.conteo_banderas}")
        self.labels["mines"].config(text=f"Mines: {self.tablero.minas_totales}")

    def updateTimer(self):
        """Actualiza el cronómetro."""
        ts = "00:00:00"
        if self.startTime is not None:
            delta = datetime.now() - self.startTime
            secs = int(delta.total_seconds())
            hours, remainder = divmod(secs, 3600)
            minutes, seconds = divmod(remainder, 60)
            ts = f"{hours:02}:{minutes:02}:{seconds:02}"

        self.labels["time"].config(text=ts)
        self.frame.after(100, self.updateTimer) # Repetir cada 100ms

    def onClickWrapper(self, x, y):
        """Closure para el evento de clic izquierdo."""
        # El argumento 'event' es esperado por tkinter
        return lambda event: self.onClick(x, y)

    def onRightClickWrapper(self, x, y):
        """Closure para el evento de clic derecho."""
        # El argumento 'event' es esperado por tkinter
        return lambda event: self.onRightClick(x, y)

    def onClick(self, x, y):
        """Manejador del evento de clic izquierdo."""
        if self.tablero.juego_terminado:
            return

        if self.startTime is None:
            self.startTime = datetime.now()

        celda_logica = self.tablero.get_celda(x, y)

        if celda_logica.estado == STATE_FLAGGED or celda_logica.estado == STATE_CLICKED:
            return

        if celda_logica.es_mina:
            self.tablero.juego_terminado = True
            self.tablero.victoria = False
            self.gameOver()
            return

        celdas_actualizadas = self.tablero.revelar_celda(x, y)
        for celda in celdas_actualizadas:
            self.actualizar_boton(celda.x, celda.y)

        if self.tablero.juego_terminado and self.tablero.victoria:
            self.gameOver()

    def onRightClick(self, x, y):
        """Manejador del evento de clic derecho (marcar)."""
        if self.tablero.juego_terminado:
            return

        if self.startTime is None:
            self.startTime = datetime.now()

        celda_actualizada = self.tablero.marcar_celda(x, y)

        if celda_actualizada:
            self.actualizar_boton(x, y)
            boton = self.botones[x][y]
            if celda_actualizada.estado == STATE_FLAGGED:
                boton.unbind(BTN_CLICK)
            else:
                boton.bind(BTN_CLICK, self.onClickWrapper(x, y))

        self.refreshLabels()

    def actualizar_boton(self, x, y):
        """Sincroniza la imagen de un botón con el estado de la celda."""
        celda_logica = self.tablero.get_celda(x, y)
        boton = self.botones[x][y]

        if celda_logica.estado == STATE_DEFAULT:
            boton.config(image=self.images["plain"])
        elif celda_logica.estado == STATE_FLAGGED:
            boton.config(image=self.images["flag"])
        elif celda_logica.estado == STATE_CLICKED:
            if celda_logica.minas_vecinas == 0:
                boton.config(image=self.images["clicked"])
            else:
                try:
                    boton.config(image=self.images["numbers"][celda_logica.minas_vecinas - 1])
                except IndexError:
                    print(f"Error: minas_vecinas fuera de rango {celda_logica.minas_vecinas}")

    def gameOver(self):
        """Maneja el fin del juego (victoria o derrota)."""
        # Mostrar todas las minas y banderas incorrectas
        for x in range(0, self.tablero.size_x):
            for y in range(0, self.tablero.size_y):
                celda = self.tablero.get_celda(x, y)
                boton = self.botones[x][y]

                if not celda.es_mina and celda.estado == STATE_FLAGGED:
                    boton.config(image=self.images["wrong"])
                if celda.es_mina and celda.estado != STATE_FLAGGED:
                    boton.config(image=self.images["mine"])

        self.root.update()

        msg = "¡Ganaste! ¿Jugar de nuevo?" if self.tablero.victoria else "¡Perdiste! ¿Jugar de nuevo?"
        # Usar el módulo messagebox importado
        if messagebox.askyesno("Fin del Juego", msg):
            self.restart()
        else:
            self.root.quit()