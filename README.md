# 💣 Buscaminas (Minesweeper) + Agentes IA (RL & CSP)

[![CI](https://github.com/fmpalmab/proyecto-buscaminas/actions/workflows/ci.yml/badge.svg)](https://github.com/fmpalmab/proyecto-buscaminas/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: standard](https://img.shields.io/badge/code%20style-pep8-green.svg)](https://pep8.org/)

Implementación moderna del clásico juego **Buscaminas (Minesweeper)** desarrollada en Python con arquitectura desacoplada, interfaz gráfica en `Tkinter`, modo consola ASCII headless, y múltiples agentes de **Inteligencia Artificial**:
1. **Agente Q-Learning Aproximado:** Aprendizaje por Refuerzo con Aproximación Lineal de Funciones.
2. **Agente Deductivo CSP:** Solucionador determinista basado en Satisfacción de Restricciones.
3. **Línea Base Aleatoria:** Agente estocástico para contraste empírico.

---

## 🏗️ Arquitectura del Proyecto

El código está estructurado como un paquete Python estándar (`buscaminas`), manteniendo compatibilidad total con los scripts raíz originales:

```
proyecto-buscaminas/
├── .github/
│   └── workflows/
│       └── ci.yml               # Pipeline de integración continua (Pytest en 3.10, 3.11, 3.12)
├── buscaminas/                  # Paquete principal modular
│   ├── __init__.py              # Exportaciones públicas de API
│   ├── __main__.py              # Punto de entrada ejecutable (python -m buscaminas)
│   ├── agent.py                 # Agentes RL (Q-Learning), Heurístico (CSP) y Aleatorio
│   ├── cli.py                   # Interfaz de línea de comandos unificada
│   ├── evaluator.py             # Rutinas de benchmarking y generación de gráficos
│   ├── gui.py                   # Interfaz Tkinter desacoplada con soporte headless
│   ├── model.py                 # Modelo lógico, flood-fill, auto-flagging y rewards RL
│   └── trainer.py               # Bucle de entrenamiento y guardado de pesos
├── images/                      # Sprites gráficos del juego (.gif)
├── tests/                       # Suite de pruebas unitarias (Pytest)
│   ├── test_agent.py
│   ├── test_cli.py
│   ├── test_evaluator.py
│   ├── test_heuristics.py
│   └── test_model.py
├── pyproject.toml               # Configuración de empaquetado moderno (PEP 517/621)
├── mi_agente_entrenado.pkl      # Pesos serializados del agente RL (pickle)
├── mi_agente_entrenado.json     # Pesos y metadatos exportados en formato JSON legible
├── comparacion_final.png        # Gráfico comparativo de desempeño entre agentes
├── metricas_entrenamiento.png   # Evolución de win rate, recompensas y decaimiento de epsilon
├── main.py                      # Shim compatible: Ejecutar juego interactivo
├── entrenar.py                  # Shim compatible: Entrenar agente RL
├── evaluar.py                   # Shim compatible: Ejecutar benchmark cuantitativo
└── ver_agente.py                # Shim compatible: Demo en tiempo real en GUI
```

---

## ⚡ Instalación Rápida

Requiere **Python 3.10+**.

```bash
# Clonar repositorio
git clone https://github.com/fmpalmab/proyecto-buscaminas.git
cd proyecto-buscaminas

# Instalar dependencias base
pip install -e .

# O instalar con dependencias de desarrollo para pruebas
pip install -e ".[dev]"
```

---

## 🎮 Modos de Ejecución

### 1. Interfaz de Comandos Unificada (`buscaminas`)

```bash
# Jugar en interfaz gráfica (Tkinter)
python -m buscaminas --play

# Jugar en modo terminal ASCII (ideal para SSH / entornos headless)
python -m buscaminas --ascii

# Ver a la IA resolver en modo terminal ASCII paso a paso
python -m buscaminas --auto-ascii

# Demostración gráfica del agente resolviendo el tablero en tiempo real
python -m buscaminas --demo

# Entrenar el agente de Q-Learning con parámetros personalizados
python -m buscaminas --train --episodes 10000 --size 6 --mines 0.15

# Evaluar cuantitativamente todos los agentes y generar reporte
python -m buscaminas --eval --eval-games 1000 --size 6 --mines 0.15
```

### 2. Scripts Raíz (Compatibilidad Histórica)

Todos los comandos originales continúan funcionando exactamente igual:

```bash
python main.py        # Abrir juego manual
python entrenar.py    # Entrenar agente Q-Learning
python evaluar.py     # Comparar agentes contra baseline aleatoria
python ver_agente.py  # Ver demostración gráfica de la IA
```

---

## 🧠 Algoritmos e Inteligencia Artificial

### Q-Learning Aproximado (Linear Function Approximation)

Dado que el espacio de estados de Buscaminas es combinatoriamente inmenso, el agente no utiliza tablas `Q(s, a)` discretas, sino una **aproximación lineal ponderada**:

$$Q(s, a) = \sum_{i=0}^{5} w_i \cdot f_i(s, a)$$

Donde cada $f_i(s, a)$ corresponde a una característica topológica local de la celda elegida $(x, y)$:
- **$f_0$ (Bias):** Término independiente constante ($1.0$).
- **$f_1$ (Vecinos Ocultos):** Proporción de casillas contiguas no descubiertas.
- **$f_2$ (Vecinos Bandera):** Cantidad ponderada de banderas adyacentes.
- **$f_3$ (Presencia de Pista):** Indicador binario si la celda limita con un número revelado.
- **$f_4$ (Suma de Pistas):** Suma escalar de las restricciones numéricas circundantes.
- **$f_5$ (Vecino Satisfecho):** Activación fuerte si algún número adyacente ya tiene todas sus minas marcadas por banderas (indicando que la celda es matemáticamente segura).

La regla de actualización de pesos por gradiente descendente temporal TD(0) es:

$$w_i \leftarrow w_i + \alpha \cdot \left[ r + \gamma \max_{a'} Q(s', a') - Q(s, a) \right] \cdot f_i(s, a)$$

### Solucionador Deductivo CSP (Constraint Satisfaction)

El agente heurístico modela el tablero local como un sistema de ecuaciones lineales booleanas sobre las celdas ocultas frontera:

$$\sum_{c \in \text{Ocultos}(v)} c = \text{Pista}(v) - \text{Banderas}(v)$$

Aplica:
1. **Regla de Vecino Satisfecho:** Si $\text{Pista}(v) = \text{Banderas}(v)$, cualquier vecino oculto es seguro ($P(\text{mina}) = 0$).
2. **Deducción de Subconjuntos:** Si los vecinos ocultos del conjunto $A$ están contenidos en $B$ con idéntica demanda de minas residuales, la diferencia $B \setminus A$ es 100% segura.
3. **Mínimo Riesgo:** En caso de requerir una conjetura estocástica forzada, minimiza la probabilidad condicional de mina.

---

## 📊 Resultados y Benchmark

Evaluación sobre **1,000 partidas** en tablero $6 \times 6$ con 15% de minas:

| Agente | Tipo | Tasa de Victoria | Pasos Promedio |
|---|---|:---:|:---:|
| **Agente Aleatorio** | Baseline estocástica | ~11 - 17% | 5.4 - 21.7 |
| **Agente IA (Q-Learning)** | Aprendizaje por Refuerzo | **~65 - 77%** | 7.4 - 8.3 |
| **Agente Heurístico (CSP)** | Deducción lógica determinista | **~77 - 82%** | 9.0 - 9.3 |
| **Humano (Referencia)** | Jugador experimentado | ~80% | ~9.0 |

---

## 🧪 Pruebas Automatizadas

La suite de pruebas cubre modelos, lógica de reglas, flood-fill, auto-flagging, serialización, agentes y CLI:

```bash
pytest -v
```

---

## 📜 Licencia

Distribuido bajo la Licencia **MIT**. Desarrollado originalmente en la FCFM, Universidad de Chile.