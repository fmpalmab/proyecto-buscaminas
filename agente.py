import random
import pickle

class AgenteQLearning:
    def __init__(self, actions, epsilon=0.9, alpha=0.1, gamma=0.9):
        self.q_table = {} # La "Memoria" del agente: Dict[Estado, Dict[Accion, Valor]]
        self.actions = actions # Lista de coordenadas posibles [(0,0), (0,1)...]
        self.epsilon = epsilon # Probabilidad de explorar
        self.alpha = alpha     # Tasa de aprendizaje
        self.gamma = gamma     # Factor de descuento

    def get_q_value(self, state, action):
        return self.q_table.get(state, {}).get(action, 0.0)

    def elegir_accion(self, state):
        """Epsilon-Greedy: Explora o Explota"""
        if random.random() < self.epsilon:
            return random.choice(self.actions) # Explorar
        
        # Explotar: Buscar la mejor acción conocida
        state_actions = self.q_table.get(state, {})
        if not state_actions:
            return random.choice(self.actions)
        
        # Encontrar la acción con el valor Q máximo
        max_q = max(state_actions.values())
        mejores_acciones = [acc for acc, q in state_actions.items() if q == max_q]
        
        # Si hay empate, elegir una al azar de las mejores
        if mejores_acciones:
            return random.choice(mejores_acciones)
        return random.choice(self.actions)

    def aprender(self, state, action, reward, next_state):
        """Actualiza la Q-Table usando la ecuación de Bellman"""
        current_q = self.get_q_value(state, action)
        
        # Calcular max Q del siguiente estado
        next_state_actions = self.q_table.get(next_state, {})
        max_next_q = max(next_state_actions.values()) if next_state_actions else 0.0

        # Fórmula Q-Learning
        new_q = current_q + self.alpha * (reward + (self.gamma * max_next_q) - current_q)

        # Guardar en la tabla
        if state not in self.q_table:
            self.q_table[state] = {}
        self.q_table[state][action] = new_q

    def guardar_agente(self, filename="q_table.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(self.q_table, f)

    def cargar_agente(self, filename="q_table.pkl"):
        try:
            with open(filename, "rb") as f:
                self.q_table = pickle.load(f)
        except FileNotFoundError:
            print("No se encontró archivo de agente guardado.")