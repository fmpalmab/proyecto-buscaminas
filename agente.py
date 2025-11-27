# agente.py
import random

class AgenteQLearningAproximado:
    def __init__(self, actions, epsilon=0.9, alpha=0.01, gamma=0.9):
        self.actions = actions
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma
        
        # Pesos para las características:
        # w0: Bias, w1: Vecinos Ocultos, w2: Vecinos Bandera, 
        # w3: Pistas Bajas, w4: Pistas Altas, w5: Vecino Satisfecho (CRUCIAL)
        self.weights = [0.0] * 6 

    def get_features(self, state, x, y):
        """
        Extrae características locales de la celda (x, y) dado el estado del tablero.
        state es una tupla de tuplas (matriz).
        """
        rows = len(state)
        cols = len(state[0])
        
        # Definir vecindad
        vecinos_coords = []
        for i in range(max(0, x-1), min(rows, x+2)):
            for j in range(max(0, y-1), min(cols, y+2)):
                if (i, j) != (x, y):
                    vecinos_coords.append((i, j))

        n_ocultos = 0
        n_banderas = 0
        suma_pistas = 0
        es_vecino_satisfecho = 0 # Característica más fuerte

        for (nx, ny) in vecinos_coords:
            val = state[nx][ny]
            if val == -1: # Oculto
                n_ocultos += 1
            elif val == -2: # Bandera
                n_banderas += 1
            else: # Es un número (0-8)
                suma_pistas += val
                
                # --- Lógica de "Satisfecho" ---
                # Si un vecino tiene valor N y ya tiene N banderas alrededor,
                # entonces todas sus otras celdas ocultas (incluyendo yo) son seguras.
                # Necesitamos contar las banderas alrededor de ESE vecino nx, ny
                banderas_vecino = 0
                for vx in range(max(0, nx-1), min(rows, nx+2)):
                    for vy in range(max(0, ny-1), min(cols, ny+2)):
                        if (vx, vy) != (nx, ny) and state[vx][vy] == -2:
                            banderas_vecino += 1
                
                if banderas_vecino == val:
                    es_vecino_satisfecho = 1

        # Vector de características (normalizado simplificado)
        return [
            1.0,                        # f0: Bias
            n_ocultos * 0.1,            # f1: Cantidad vecinos ocultos
            n_banderas * 0.5,           # f2: Cantidad vecinos bandera
            (suma_pistas > 0),          # f3: ¿Tiene algún número cerca? (Binario)
            suma_pistas * 0.1,          # f4: Suma total de números vecinos
            es_vecino_satisfecho * 2.0  # f5: ¿Estoy al lado de un número ya resuelto?
        ]

    def get_q_value(self, state, action):
        """Producto punto: Q(s, a) = weights * features(s, a)"""
        x, y = action
        features = self.get_features(state, x, y)
        q_val = sum(w * f for w, f in zip(self.weights, features))
        return q_val

    def elegir_accion(self, state):
        # Filtra acciones válidas (celdas no reveladas ni banderas)
        # Nota: state[x][y] es -1 (oculto) o -2 (bandera) o >=0 (revelado)
        acciones_validas = [
            (x, y) for x, y in self.actions 
            if state[x][y] == -1  # Solo elegimos celdas Ocultas (no banderas)
        ]
        
        if not acciones_validas:
            return random.choice(self.actions) # Fallback raro

        if random.random() < self.epsilon:
            return random.choice(acciones_validas)

        # Explotar: Calcular Q para cada acción posible y elegir la mejor
        best_q = -float('inf')
        best_actions = []

        for accion in acciones_validas:
            q = self.get_q_value(state, accion)
            if q > best_q:
                best_q = q
                best_actions = [accion]
            elif q == best_q:
                best_actions.append(accion)
        
        return random.choice(best_actions)

    def aprender(self, state, action, reward, next_state):
        """Actualización de pesos por Descenso de Gradiente (Linear Q-Learning)"""
        x, y = action
        
        # 1. Q actual
        current_q = self.get_q_value(state, action)
        features = self.get_features(state, x, y)

        # 2. Max Q futuro (sobre acciones válidas en next_state)
        acciones_futuras = [
            (ax, ay) for ax, ay in self.actions 
            if next_state[ax][ay] == -1
        ]
        
        max_next_q = 0.0
        if acciones_futuras:
            max_next_q = max(self.get_q_value(next_state, a) for a in acciones_futuras)

        # 3. Calcular error (TD Error)
        td_target = reward + (self.gamma * max_next_q)
        td_error = td_target - current_q

        # 4. Actualizar pesos
        # wi = wi + alpha * error * fi
        for i in range(len(self.weights)):
            self.weights[i] += self.alpha * td_error * features[i]

    def guardar_agente(self, filename="agente_linear.pkl"):
        import pickle
        with open(filename, "wb") as f:
            pickle.dump(self.weights, f)
    
    def cargar_agente(self, filename="agente_linear.pkl"):
        import pickle
        try:
            with open(filename, "rb") as f:
                self.weights = pickle.load(f)
            print(f"Modelo cargado exitosamente desde {filename}")
        except FileNotFoundError:
            print(f"No se encontró el archivo {filename}. Se continuará con pesos iniciales.")
        except Exception as e:
            print(f"Error al cargar el agente: {e}")