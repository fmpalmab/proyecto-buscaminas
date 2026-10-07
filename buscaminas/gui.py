"""
Interfaz gráfica Tkinter para Buscaminas y visualizador del agente IA.
Incluye resolución robusta de rutas para imágenes y manejo de errores.
"""

from __future__ import annotations

import platform
import tkinter as tk
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from buscaminas.model import (
    Tablero,
    Celda,
    STATE_DEFAULT,
    STATE_CLICKED,
    STATE_FLAGGED,
)
from buscaminas.agent import AgenteQLearningAproximado

# Botones según sistema operativo
BTN_CLICK = "<Button-1>"
BTN_FLAG = "<Button-2>" if platform.system() == "Darwin" else "<Button-3>"


def find_image_dir() -> Optional[Path]:
    """Busca recursivamente la carpeta de imágenes del proyecto."""
    candidates = [
        Path.cwd() / "images",
        Path(__file__).resolve().parent.parent / "images",
        Path(__file__).resolve().parent / "images",
    ]
    for c in candidates:
        if c.is_dir() and (c / "tile_plain.gif").is_file():
            return c
    return None


class MinesweeperGUI:
    """Manejador de la interfaz gráfica y eventos de usuario."""

    def __init__(self, root: tk.Tk, tablero: Tablero) -> None:
        self.root: tk.Tk = root
        self.tablero: Tablero = tablero
        self.images: Dict[str, Any] = {}
        self.has_images: bool = False

        self._load_images()

        self.frame: tk.Frame = tk.Frame(self.root)
        self.frame.pack(padx=8, pady=8)

        # Labels informativos
        self.labels: Dict[str, tk.Label] = {
            "time": tk.Label(self.frame, text="00:00:00", font=("Helvetica", 10, "bold")),
            "mines": tk.Label(self.frame, text="Minas: 0", font=("Helvetica", 9)),
            "flags": tk.Label(self.frame, text="Banderas: 0", font=("Helvetica", 9)),
        }
        self.labels["time"].grid(row=0, column=0, columnspan=self.tablero.size_y, pady=4)
        col_span = max(1, self.tablero.size_y // 2)
        self.labels["mines"].grid(row=self.tablero.size_x + 1, column=0, columnspan=col_span, pady=4)
        self.labels["flags"].grid(
            row=self.tablero.size_x + 1,
            column=col_span,
            columnspan=col_span,
            pady=4,
        )

        self.botones: Dict[int, Dict[int, tk.Button]] = {}
        self.startTime: Optional[datetime] = None

        self.setup_ui_botones()
        self.refreshLabels()
        self.updateTimer()

    def _load_images(self) -> None:
        img_dir = find_image_dir()
        if img_dir is not None:
            try:
                self.images = {
                    "plain": tk.PhotoImage(file=str(img_dir / "tile_plain.gif")),
                    "clicked": tk.PhotoImage(file=str(img_dir / "tile_clicked.gif")),
                    "mine": tk.PhotoImage(file=str(img_dir / "tile_mine.gif")),
                    "flag": tk.PhotoImage(file=str(img_dir / "tile_flag.gif")),
                    "wrong": tk.PhotoImage(file=str(img_dir / "tile_wrong.gif")),
                    "numbers": [
                        tk.PhotoImage(file=str(img_dir / f"tile_{i}.gif")) for i in range(1, 9)
                    ],
                }
                self.has_images = True
            except Exception as e:
                print(f"[Aviso] No se pudieron cargar imágenes completas: {e}. Usando modo texto.")
                self.has_images = False
        else:
            self.has_images = False

    def setup_ui_botones(self) -> None:
        """Inicializa los botones de la grilla."""
        for x in range(self.tablero.size_x):
            self.botones[x] = {}
            for y in range(self.tablero.size_y):
                if self.has_images:
                    btn = tk.Button(self.frame, image=self.images["plain"], width=24, height=24)
                else:
                    btn = tk.Button(self.frame, text=" ", width=3, height=1)

                btn.bind(BTN_CLICK, self.crear_handler_click(x, y))
                btn.bind(BTN_FLAG, self.crear_handler_flag(x, y))
                btn.grid(row=x + 1, column=y, padx=1, pady=1)
                self.botones[x][y] = btn

    def crear_handler_click(self, x: int, y: int):
        return lambda event: self.onClick(x, y)

    def crear_handler_flag(self, x: int, y: int):
        return lambda event: self.onRightClick(x, y)

    def restart(self) -> None:
        """Reinicia la partida y la interfaz."""
        self.tablero.reiniciar()
        self.startTime = None
        for x in range(self.tablero.size_x):
            for y in range(self.tablero.size_y):
                btn = self.botones[x][y]
                if self.has_images:
                    btn.config(image=self.images["plain"], text="")
                else:
                    btn.config(text=" ", relief=tk.RAISED)
                btn.bind(BTN_CLICK, self.crear_handler_click(x, y))
                btn.bind(BTN_FLAG, self.crear_handler_flag(x, y))
        self.refreshLabels()

    def refreshLabels(self) -> None:
        self.labels["flags"].config(text=f"Banderas: {self.tablero.conteo_banderas}")
        self.labels["mines"].config(text=f"Minas: {self.tablero.minas_totales}")

    def updateTimer(self) -> None:
        if self.startTime is not None and not self.tablero.juego_terminado:
            now = datetime.now()
            delta = now - self.startTime
            horas, rem = divmod(int(delta.total_seconds()), 3600)
            mins, segs = divmod(rem, 60)
            self.labels["time"].config(text=f"{horas:02d}:{mins:02d}:{segs:02d}")
        self.root.after(1000, self.updateTimer)

    def onClick(self, x: int, y: int) -> None:
        if self.startTime is None:
            self.startTime = datetime.now()

        celda = self.tablero.get_celda(x, y)
        if celda is None or celda.estado != STATE_DEFAULT or self.tablero.juego_terminado:
            return

        if self.tablero.primer_movimiento:
            self.tablero._generar_minas_seguras(x, y)
            self.tablero.primer_movimiento = False
            self.refreshLabels()

        if celda.es_mina:
            self.tablero.juego_terminado = True
            self.gameOver(False)
            return

        celdas_reveladas = self.tablero.revelar_celda(x, y)
        for c in celdas_reveladas:
            self.actualizar_boton(c.x, c.y)

        if self.tablero.juego_terminado and self.tablero.victoria:
            self.gameOver(True)

    def onRightClick(self, x: int, y: int) -> None:
        if self.tablero.juego_terminado:
            return
        celda = self.tablero.marcar_celda(x, y)
        if celda is not None:
            self.actualizar_boton(x, y)
            self.refreshLabels()

    def actualizar_boton(self, x: int, y: int) -> None:
        celda = self.tablero.get_celda(x, y)
        if celda is None:
            return
        btn = self.botones[x][y]

        if celda.estado == STATE_DEFAULT:
            if self.has_images:
                btn.config(image=self.images["plain"], text="")
            else:
                btn.config(text=" ", relief=tk.RAISED)
        elif celda.estado == STATE_FLAGGED:
            if self.has_images:
                btn.config(image=self.images["flag"], text="")
            else:
                btn.config(text="🚩", relief=tk.RAISED)
        elif celda.estado == STATE_CLICKED:
            if celda.es_mina:
                if self.has_images:
                    btn.config(image=self.images["mine"], text="")
                else:
                    btn.config(text="💥", relief=tk.SUNKEN)
            elif celda.minas_vecinas == 0:
                if self.has_images:
                    btn.config(image=self.images["clicked"], text="")
                else:
                    btn.config(text="", relief=tk.SUNKEN)
            else:
                pistas = celda.minas_vecinas
                if self.has_images:
                    btn.config(image=self.images["numbers"][pistas - 1], text="")
                else:
                    btn.config(text=str(pistas), relief=tk.SUNKEN)
            try:
                btn.unbind(BTN_CLICK)
                btn.unbind(BTN_FLAG)
            except Exception:
                pass

    def gameOver(self, victoria: bool) -> None:
        for x in range(self.tablero.size_x):
            for y in range(self.tablero.size_y):
                c = self.tablero.get_celda(x, y)
                btn = self.botones[x][y]
                if c.es_mina:
                    if not victoria and c.estado != STATE_FLAGGED:
                        if self.has_images:
                            btn.config(image=self.images["mine"])
                        else:
                            btn.config(text="💥")
                elif c.estado == STATE_FLAGGED:
                    if self.has_images:
                        btn.config(image=self.images["wrong"])
                    else:
                        btn.config(text="❌")

        titulo = "¡Victoria!" if victoria else "Fin del Juego"
        mensaje = "¡Felicidades, ganaste!" if victoria else "¡Boom! Has pisado una mina."
        print(f"[{titulo}] {mensaje}")


class AgenteGUI(MinesweeperGUI):
    """Extensión de GUI para demostración visual de agentes automáticos."""

    def __init__(self, root: tk.Tk, tablero: Tablero, agente: AgenteQLearningAproximado, velocidad_ms: int = 400) -> None:
        super().__init__(root, tablero)
        self.agente: AgenteQLearningAproximado = agente
        self.velocidad: int = velocidad_ms
        self.jugando_auto: bool = False

    def iniciar_demo(self) -> None:
        self.jugando_auto = True
        self.siguiente_movimiento()

    def siguiente_movimiento(self) -> None:
        if not self.jugando_auto or self.tablero.juego_terminado:
            return

        estado = self.tablero.get_estado_hashable()
        epsilon_prev = self.agente.epsilon
        self.agente.epsilon = 0.0
        x, y = self.agente.elegir_accion(estado)
        self.agente.epsilon = epsilon_prev

        self.onClick(x, y)

        if self.tablero.juego_terminado:
            return

        banderas_previas = {
            (i, j)
            for i in range(self.tablero.size_x)
            for j in range(self.tablero.size_y)
            if self.tablero.get_celda(i, j).estado == STATE_FLAGGED
        }

        self.tablero._auto_flag()

        nuevas_banderas = [
            (i, j)
            for i in range(self.tablero.size_x)
            for j in range(self.tablero.size_y)
            if self.tablero.get_celda(i, j).estado == STATE_FLAGGED and (i, j) not in banderas_previas
        ]

        if nuevas_banderas:
            self.root.after(self.velocidad, lambda: self.animar_banderas(nuevas_banderas))
        else:
            self.root.after(self.velocidad, self.siguiente_movimiento)

    def animar_banderas(self, lista_banderas: List[Tuple[int, int]]) -> None:
        if not lista_banderas or self.tablero.juego_terminado:
            self.siguiente_movimiento()
            return

        x, y = lista_banderas.pop(0)
        self.actualizar_boton(x, y)
        self.refreshLabels()
        self.root.after(self.velocidad, lambda: self.animar_banderas(lista_banderas))
