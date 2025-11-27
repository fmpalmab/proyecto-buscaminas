# ver_agente.py
import tkinter as tk
from juego_model import Tablero, STATE_FLAGGED
from interfaz_gui import MinesweeperGUI, BTN_CLICK
from agente import AgenteQLearningAproximado 

# --- CONFIGURACIÓN ---
SIZE = 6       
MINAS_RATIO = 0.15 
VELOCIDAD = 500  # Tiempo de espera entre acciones (ms)

class AgenteGUI(MinesweeperGUI):
    def __init__(self, root, tablero, agente):
        super().__init__(root, tablero)
        self.agente = agente
        self.jugando_auto = False

    def iniciar_demo(self):
        self.jugando_auto = True
        self.siguiente_movimiento()

    def siguiente_movimiento(self):
        """Ciclo principal de decisión del agente."""
        if not self.jugando_auto or self.tablero.juego_terminado:
            return

        # 1. Obtener estado
        estado = self.tablero.get_estado_hashable()
        
        # 2. Elegir acción (sin exploración)
        epsilon_prev = self.agente.epsilon
        self.agente.epsilon = 0 
        x, y = self.agente.elegir_accion(estado)
        self.agente.epsilon = epsilon_prev
        
        print(f"🤖 Agente decide click en: ({x}, {y})")

        # 3. Ejecutar Click
        self.onClick(x, y)

        if self.tablero.juego_terminado:
            return

        # --- LÓGICA DE AUTO-FLAG ANIMADA ---
        
        # A. Detectar qué banderas YA existían antes del auto-flag
        banderas_previas = set()
        for i in range(self.tablero.size_x):
            for j in range(self.tablero.size_y):
                if self.tablero.get_celda(i, j).estado == STATE_FLAGGED:
                    banderas_previas.add((i, j))

        # B. Ejecutar la lógica interna (el modelo se actualiza instantáneamente)
        self.tablero._auto_flag()

        # C. Detectar cuáles son las NUEVAS banderas
        nuevas_banderas = []
        for i in range(self.tablero.size_x):
            for j in range(self.tablero.size_y):
                celda = self.tablero.get_celda(i, j)
                if celda.estado == STATE_FLAGGED and (i, j) not in banderas_previas:
                    nuevas_banderas.append((i, j))

        # D. Si hay nuevas banderas, iniciar animación. Si no, seguir jugando.
        if nuevas_banderas:
            # Esperar un turno antes de empezar a poner banderas
            self.root.after(VELOCIDAD, lambda: self.animar_banderas(nuevas_banderas))
        else:
            self.root.after(VELOCIDAD, self.siguiente_movimiento)

    def animar_banderas(self, lista_banderas):
        """
        Función recursiva que pone una bandera, espera, y llama a la siguiente.
        """
        if not lista_banderas or self.tablero.juego_terminado:
            # Si se acabaron las banderas, volvemos al bucle principal del agente
            self.siguiente_movimiento()
            return

        # Sacar la siguiente coordenada de la lista
        x, y = lista_banderas.pop(0)
        
        # Actualizar visualmente esa celda específica
        print(f"🚩 Auto-Flag en: ({x}, {y})")
        self.actualizar_boton(x, y)
        self.refreshLabels()
        
        # Desvincular el clic (seguridad)
        try:
            self.botones[x][y].unbind(BTN_CLICK)
        except:
            pass

        # Programar la siguiente bandera con el retraso VELOCIDAD
        self.root.after(VELOCIDAD, lambda: self.animar_banderas(lista_banderas))

    def restart(self):
        super().restart()
        if self.jugando_auto:
            self.root.after(1000, self.siguiente_movimiento)

def main():
    root = tk.Tk()
    root.title(f"Demo Agente Buscaminas ({SIZE}x{SIZE})")

    # Inicializar
    tablero = Tablero(SIZE, SIZE, MINAS_RATIO)
    acciones = [(x, y) for x in range(SIZE) for y in range(SIZE)]
    agente = AgenteQLearningAproximado(actions=acciones)
    
    # Cargar
    try:
        agente.cargar_agente("mi_agente_entrenado.pkl")
        print("✅ Agente cargado.")
    except:
        print("❌ Error cargando agente.")
        return

    # Correr
    app = AgenteGUI(root, tablero, agente)
    root.after(1000, app.iniciar_demo)
    root.mainloop()

if __name__ == "__main__":
    main()