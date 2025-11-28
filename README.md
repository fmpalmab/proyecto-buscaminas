# Proyecto Buscaminas (Minesweeper) + Agente IA

Este repositorio contiene una implementación clásica del juego Buscaminas desarrollada en Python 3 utilizando la librería gráfica `Tkinter`. Además, el proyecto ha sido extendido con un **Agente de Inteligencia Artificial** basado en Aprendizaje por Refuerzo (Q-Learning Aproximado) capaz de aprender a resolver el tablero por sí mismo.

El proyecto fue desarrollado como parte del **Proyecto N°2** del curso **EL4203-2: Programación Avanzada** de la Facultad de Ciencias Físicas y Matemáticas (FCFM) de la Universidad de Chile.

---

## 🚀 Cómo Empezar

Sigue estos pasos para ejecutar el juego o entrenar al agente en tu máquina local.

### 1. Prerrequisitos

* **Python 3:** El juego está escrito en Python 3.
* **Tkinter:** Librería estándar de GUI. Generalmente viene preinstalada con Python.
* **Librerías para la IA:** Para ejecutar el agente y generar los gráficos, necesitas instalar las siguientes dependencias:
    ```bash
    pip install numpy matplotlib
    ```
* **Imágenes (¡Importante!):** El juego **requiere** la carpeta `images/` con todos los archivos `.gif` (`tile_plain.gif`, `tile_1.gif`, etc.) en el mismo directorio que los scripts para funcionar.

### 2. Instalación

1.  **Clona el repositorio:**
    ```bash
    git clone [https://github.com/fmpalmab/proyecto-buscaminas](https://github.com/fmpalmab/proyecto-buscaminas)
    ```
2.  **Navega a la carpeta del proyecto:**
    ```bash
    cd proyecto-buscaminas
    ```

---

## 🎮 Modos de Ejecución

Puedes ejecutar el proyecto en modo manual (humano) o utilizar los scripts de Inteligencia Artificial.

### A. Jugar Manualmente
Ejecuta el archivo principal para abrir la interfaz clásica:

```bash
python3 main.py
```
* **Clic Izquierdo:** Revela una celda.
* **Clic Derecho:** Coloca o quita una bandera.
* **Objetivo:** Revelar todas las celdas sin minas.

### B. Inteligencia Artificial (Q-Learning)

El proyecto incluye un agente capaz de aprender a jugar mediante Q-Learning con Aproximación de Funciones Lineales.

#### 1. Entrenar al Agente
Ejecuta el script de entrenamiento para que el agente juegue miles de partidas y aprenda.
```bash
python3 entrenar.py
```
* Esto generará dos archivos:
    * `mi_agente_entrenado.pkl`: El "cerebro" del agente (sus pesos guardados).
    * `metricas_entrenamiento.png`: Un gráfico mostrando su progreso (Win Rate).

#### 2. Ver al Agente Jugar (Demo)
Una vez entrenado (o si ya tienes el archivo `.pkl`), puedes ver al agente jugar en tiempo real en la interfaz gráfica.
```bash
python3 ver_agente.py
```
* El agente controlará el mouse y tomará decisiones.
* Incluye una animación de "Auto-Flag" para marcar minas evidentes.

#### 3. Evaluar Rendimiento
Compara el desempeño del agente entrenado contra un agente aleatorio.
```bash
python3 evaluar.py
```
* Generará un reporte en consola y el gráfico `comparacion_final.png`.

---

## 📂 Estructura del Proyecto

El código sigue un patrón Modelo-Vista-Controlador (MVC) y separa la lógica de IA:

### Núcleo del Juego
* **`juego_model.py` (Modelo):** Contiene la lógica pura del tablero, reglas, estados y recompensas.
* **`interfaz_gui.py` (Vista):** Maneja la interfaz gráfica `Tkinter`, imágenes y eventos.
* **`main.py`:** Punto de entrada para el juego manual.

### Inteligencia Artificial
* **`agente.py`:** Implementación de la clase `AgenteQLearningAproximado`. Define las *features* (vecinos ocultos, banderas, vecinos satisfechos) y el algoritmo de aprendizaje.
* **`entrenar.py`:** Script para entrenar al agente masivamente (sin GUI).
* **`ver_agente.py`:** Script que conecta al agente con la GUI para demostración visual.
* **`evaluar.py`:** Script para generar estadísticas comparativas.

---

## 🧠 Sobre el Agente

El agente no memoriza el tablero (lo cual es imposible dada la cantidad de combinaciones), sino que utiliza **Aproximación de Funciones Lineales**. Evalúa cada posible movimiento basándose en características locales:

1.  **Bias:** Sesgo base.
2.  **Vecinos Ocultos:** Cantidad de celdas no reveladas alrededor.
3.  **Vecinos Bandera:** Cantidad de minas marcadas alrededor.
4.  **Pistas:** Si la celda tiene números cerca.
5.  **Vecino Satisfecho (Lógica Clave):** Detecta si una celda numérica adyacente ya tiene todas sus minas identificadas, lo que hace seguro el movimiento.

---

## 👥 Autores
Proyecto desarrollado para el curso EL4203-2.