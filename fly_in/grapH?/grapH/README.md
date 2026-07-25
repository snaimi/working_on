```markdown
*This project has been created as part of the 42 curriculum by Snaimi.*

# 🛸 Capacity-Aware Dynamic Drone Simulation

An algorithmic simulation engine in Python that parses custom map configurations, calculates route costs, and manages dynamic drone routing and zone occupancy.

---

## 📌 Table of Contents
- [Description](#-description)
- [Algorithm Choices & Implementation Strategy](#-algorithm-choices--implementation-strategy)
- [Visual Representation & User Experience](#-visual-representation--user-experience)
- [Instructions](#-instructions)
- [Resources & AI Usage](#-resources--ai-usage)
- [Special Thanks](#-special-thanks)

---

## 📄 Description

The primary goal of this project is to simulate autonomous drone navigation within a constrained graph-based airspace. Drones must traverse complex network zones while adhering to real-time spatial constraints such as capacity limits per zone, varying traversal costs, and path congestion.

### Key Objectives
- Parse structured map descriptions and environment configs.
- Calculate dynamic cost metrics across custom network topographies.
- Manage spatial traversal without exceeding max capacity limits in any single zone.

---

## 🧠 Algorithm Choices & Implementation Strategy

### 1. Map & Graph Parsing
The parsing engine reads `map_des.txt`, extracting node definitions, edge connections, zone capacities, and cost factors. The environment is modeled as a weighted graph $G = (V, E)$, where vertices $V$ represent zones and edges $E$ represent travel paths.

### 2. Graph Traversal & Pathfinding
- **Path Calculation:** Algorithms such as Breadth-First Search (BFS), Depth-First Search (DFS), and **Dijkstra's Shortest Path Algorithm** are used for route generation and shortest-path calculation across weighted topologies.
- **Dynamic Costing:** Traversal costs vary depending on zone density and occupancy. Path weights are computed dynamically:
  $$\text{Cost}_{\text{zone}} = \text{Base Cost} \times f(\text{Occupancy})$$
- **Capacity Constraint Handling:** When a target zone hits its capacity ceiling, waiting penalties or path recalculations occur to prevent zone overcrowding.

---

## 👁️ Visual Representation & User Experience

The simulation provides real-time terminal output and feedback to enhance clarity during runtimes:
- **State Feedback:** Clean, step-by-step visual representations of drone positioning, active zones, and step costs.
- **Occupancy Tracking:** Clear markers indicating current zone occupancy levels, highlighting bottleneck zones before capacity limits are violated.
- **Debugging Views:** Detailed debug output available during development to step through algorithmic decisions step-by-step.

---

## 🛠️ Instructions

### Prerequisites
- **Python 3.12+**
- **uv** (Fast Python package manager)

If `uv` is not yet installed:
```bash
curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh

```

### Installation & Setup

1. **Clone the repository:**
```bash
git clone <repository-url>
cd <repository-folder>

```


2. **Install dependencies:**
Setup the virtual environment and install requirements (`pydantic`, `flake8`, `mypy`) using `uv`:
```bash
make install

```



### Makefile Rules

| Command | Action |
| --- | --- |
| `make run` | Execute main entrypoint (`new_simulation.py`) via `uv run` |
| `make debug` | Run main script under Python debugger (`pdb`) |
| `make lint` | Perform static checks (`flake8` and `mypy`) |
| `make lint-strict` | Perform strict `mypy` type checking |
| `make clean` | Clean build artifacts, caches, and `.venv` |
| `make help` | Show all available commands |

---

## 📚 Resources & AI Usage

### Classic References & Documentation

* [Python 3.12 Official Documentation](https://docs.python.org/3/)
* [Graph Theory & Traversal Algorithms - GeeksforGeeks](https://www.geeksforgeeks.org/graph-data-structure-and-algorithms/)
* [uv Package Manager Guide](https://docs.astral.sh/uv/)

### YouTube Video Tutorials (Dijkstra's Algorithm & Simulation)

* 🎥 **Dijkstra's Algorithm Concept & Intuition:** [Computerphile - Dijkstra's Algorithm](https://www.google.com/search?q=https://www.youtube.com/watch%3Fv%3D104310) — Great breakdown of Dijkstra's algorithm logic and graph traversal.
* 🎥 **Dijkstra Visualized Step-by-Step:** [Dijkstra's Algorithm Visualized](https://www.youtube.com/watch?v=-p6_jQgsbTU) — A clear visual walkthrough showing priority queues, edge relaxation, and shortest path calculations.
* 🎥 **Python Dijkstra Implementation:** [Dijkstra's Algorithm in Python](https://www.youtube.com/watch?v=u33NM1pZvoM) — Practical guide on implementing Dijkstra using Python's `heapq` library.

### AI Usage Disclosure

AI tools (Large Language Models) were utilized during the development of this project for the following specific tasks:

* **Makefile Optimization:** Refining build targets, syntax formatting (tab spacing rules), and integrating `uv` runner commands.
* **Documentation:** Structuring and drafting the official project `README.md` according to the 42 curriculum standards.
* **Code Linting Setup:** Assisting with proper `.flake8` configuration to ignore virtual environments (`.venv`).

---

## ❤️ Special Thanks

Special thanks and deep gratitude to **1337 School**—its administration, staff, and vibrant student community. The peer-learning methodology, relentless problem-solving spirit, and supportive environment continue to inspire and drive high-quality engineering standards throughout this project! 🚀

```

```