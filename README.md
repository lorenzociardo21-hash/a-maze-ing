# A-Maze-ing

*This project has been created as part of the 42 curriculum by lciardo, lgreco.*

---

## Description

**A-Maze-ing** is a Python terminal application that randomly generates mazes, solves them, and renders the result visually in the terminal using colored ASCII art. The project implements three classic maze generation algorithms (Kruskal's, Prim's, and DFS/recursive backtracker), two solving algorithms (a custom greedy mix and A*), and an interactive terminal menu that lets the user regenerate, visualize, and customize the maze in real time.

A core feature is the embedded **"42" pattern** — a set of fully walled cells shaped like the number 42 — placed at the center of every maze large enough to fit it.

The maze generation logic is encapsulated in a standalone, pip-installable Python package (`maze_gen`) for reuse in other projects.

---

## Project Structure

```
a_maze_ing.py          # Main entry point
config.txt             # Default configuration file
maze.txt               # Example output file (generated)
Makefile               # Automation of common tasks
pyproject.toml         # Build configuration for the mazegen package
requirements.txt       # Project dependencies

maze_gen/
    __init__.py
    generator.py       # MazeGenerator class (reusable package)

src/
    __init__.py
    display.py         # Terminal rendering and color management
    exporter.py        # Output file writer
    parser.py          # Config file parser and mazeconfig class
    settings.py        # Runtime config editor
    solver.py          # Maze solving algorithms
```

---

## Instructions

### Requirements

- Python 3.10 or later
- `flake8` and `mypy` (see `requirements.txt`)

### Installation

```bash
make install
```

This installs the dependencies listed in `requirements.txt` using pip.

### Running

```bash
make run
# or directly:
python3 a_maze_ing.py config.txt
```

The program takes exactly one argument: the path to a configuration file.

### Debug Mode

```bash
make debug
```

Runs the main script under Python's built-in `pdb` debugger.

### Linting

```bash
make lint         # flake8 + mypy with standard flags
make lint-strict  # flake8 + mypy --strict
```

### Cleaning

```bash
make clean
```

Removes `__pycache__`, `.mypy_cache`, and `.pytest_cache` directories.

---

## Configuration File Format

The configuration file uses one `KEY=VALUE` pair per line. Lines beginning with `#` are treated as comments and ignored. All keys are mandatory.

| Key | Description | Example |
|-----|-------------|---------|
| `WIDTH` | Maze width in number of cells | `WIDTH=14` |
| `HEIGHT` | Maze height in number of cells | `HEIGHT=14` |
| `ENTRY` | Entry point coordinates `x,y` | `ENTRY=0,0` |
| `EXIT` | Exit point coordinates `x,y` | `EXIT=14,14` |
| `OUTPUT_FILE` | Name of the output file to write | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | Whether to generate a perfect maze (single path) | `PERFECT=False` |
| `SEED` | Random seed for reproducibility; use `None` for random | `SEED=None` |

Example `config.txt`:

```
#Maze width (number of cells)
WIDTH=14
#Maze height
HEIGHT=14

#Entry coordinates (x, y)
ENTRY=0, 0
#Exit coordinates (x, y)
EXIT=14,14
#Output filename
OUTPUT_FILE=maze.txt
#Is the maze perfect?
PERFECT=False
#Seed of generation
SEED=None
```

---

## Output File Format

The maze is written to the output file one row per line, with one hexadecimal digit per cell. Each hex digit encodes which walls are present using bitflags:

| Bit | Direction |
|-----|-----------|
| 0 (LSB) | North |
| 1 | East |
| 2 | South |
| 3 | West |

A bit value of `1` means the wall is closed; `0` means open.

After an empty line, three additional lines are appended:
1. Entry coordinates (`x,y`)
2. Exit coordinates (`x,y`)
3. The solution path as a sequence of `N`, `E`, `S`, `W` characters

Example:
```
BD1111793B97957
812AEC144283C53
...

0,0
14,14
SEESSSESSSSEESSSESESEEESENNEESSE
```

---

## Maze Generation Algorithms

Three algorithms are available and selectable at runtime via the interactive menu:

### 1. Kruskal's Algorithm (default)
All possible walls between adjacent cells are collected into a list and shuffled randomly. Walls are then removed one by one if the two cells they separate belong to different sets (using a union-find / disjoint-set structure). This guarantees a perfect spanning tree with no loops.

**Why Kruskal's?** It produces mazes with a good mix of long corridors and short dead ends, is straightforward to implement correctly with union-find, and yields visually interesting results. It also supports the "imperfect" mode cleanly by adding a post-processing wall-removal pass.

### 2. Prim's Algorithm
Starting from the entry cell, a frontier of walls to adjacent unvisited cells is maintained. A random wall from this frontier is selected, and if the neighbour hasn't been visited, the wall is removed and the neighbour's walls are added to the frontier. This produces mazes that tend to have many short branches radiating from the start.

### 3. DFS / Recursive Backtracker
A stack-based depth-first search from the entry cell. At each step, a random unvisited neighbour is chosen, the wall removed, and the neighbour pushed onto the stack. When no unvisited neighbours exist, the algorithm backtracks. This produces mazes with very long, winding corridors and few dead ends.

### Imperfect Mazes (`PERFECT=False`)
After any algorithm completes, an additional 15% of remaining internal walls are randomly removed, creating loops and multiple paths between cells.

### 3×3 Open Area Prevention
All three algorithms include a `square_3x3` check that prevents any 3×3 (or larger) open area from forming, satisfying the subject requirement that corridors can be at most 2 cells wide.

---

## Maze Solving Algorithms

Two solvers are available and switchable at runtime:

### Custom Greedy Mix (`maze_res_mix_algo`)
A greedy depth-first approach. At each step, the algorithm picks the unvisited neighbour that brings it closest to the exit (Euclidean distance). It backtracks when stuck. A post-processing `check_stack_none` pass then shortens the path by detecting shortcuts between non-adjacent cells that share an open wall.

### A* (`maze_res_astar`)
A standard A* implementation using Euclidean distance as the heuristic and step count as the cost. It guarantees the shortest path. The open set is maintained as a sorted list (re-sorted after each insertion).

---

## Visual Representation

The terminal rendering uses ANSI escape codes to draw the maze as colored block characters (`██`). Each cell is drawn as a 3×3 character block (top row, middle row, bottom row), where walls appear in the wall color and open passages in the corridor color.

Special cells:
- **Entry**: bright green
- **Exit**: bright red
- **42 pattern cells**: a separate accent color (default yellow)
- **Solution path**: highlighted in green when shown

### Interactive Menu Options

| Key | Action |
|-----|--------|
| `1` | Generate a new maze (disabled if SEED is set) |
| `2` | Toggle solution path visibility (animated reveal) |
| `3` | Cycle the color of walls, corridors, or the 42 pattern |
| `4` | Switch generation algorithm (Kruskal / Prim / DFS) |
| `5` | Display the current seed |
| `6` | Edit any configuration setting live |
| `7` | Switch solving algorithm (custom greedy / A*) |
| `8` | Quit |

---

## The "42" Pattern

When the maze is at least 10 cells wide and 7 cells tall, a "42" shape is carved into the center of the grid using fully walled cells (value `0xF` / `15`). These cells are never connected to the rest of the maze and are rendered in the accent color. The pattern is defined as a set of relative coordinates in `parser.py` and is computed at maze initialization time.

If the maze is too small to fit the pattern, a message is printed and the pattern is omitted.

---

## Reusable Module: `maze_gen`

The `MazeGenerator` class in `maze_gen/generator.py` is designed to be used independently of the main application. It is packaged as a pip-installable module.

### Installation

```bash
pip install mazegen-0.1.0-py3-none-any.whl
# or from source:
pip install .
```

### Basic Usage

```python
from maze_gen.generator import MazeGenerator
from src.parser import mazeconfig

# Build a minimal config dictionary
data = {
    "WIDTH": "20",
    "HEIGHT": "15",
    "ENTRY": "0,0",
    "EXIT": "19,14",
    "OUTPUT_FILE": "out.txt",
    "PERFECT": "True",
    "SEED": "None",
}
settings = mazeconfig(data)
gen = MazeGenerator(settings)

# Generate using any of the three algorithms
grid, seed = gen.generate_maze_kruskal()
# grid, seed = gen.generate_maze_prims()
# grid, seed = gen.generate_maze_dfs()

# grid is a list[list[int]] where each int encodes walls as bitflags
# seed is the integer seed that was used (useful for reproducibility)
print(f"Generated with seed: {seed}")
print(f"Grid dimensions: {len(grid)} rows x {len(grid[0])} cols")
```

### Custom Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `width` | `int` | Number of columns |
| `height` | `int` | Number of rows |
| `entry` | `tuple[int, int]` | Entry cell coordinates |
| `exit` | `tuple[int, int]` | Exit cell coordinates |
| `perfect` | `bool` | Enforce single-path maze |
| `seed` | `str \| None` | `"None"` for random, or a numeric string |
| `pattern_cells` | `set[tuple[int,int]]` | Cells to treat as blocked (used for the 42 pattern) |

### Accessing the Structure

The returned `grid` is a `list[list[int]]` indexed as `grid[y][x]`. Each cell's integer value encodes its walls as bitflags (bit 0 = North, bit 1 = East, bit 2 = South, bit 3 = West). A set bit means that wall is **closed**.

To solve the generated maze, use the functions in `src/solver.py`:

```python
from src.solver import maze_res_astar, maze_res_mix_algo

solution = maze_res_astar(gen, grid)
# solution is a list[tuple[int, int, str | None]]
# each tuple is (x, y, direction) where direction is 'N','E','S','W' or None for the last cell
for x, y, direction in solution:
    print(f"  ({x},{y}) -> {direction}")
```

---

## Resources

- [Maze generation algorithms — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Kruskal's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Kruskal%27s_algorithm)
- [Prim's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Prim%27s_algorithm)
- [A* search algorithm — Wikipedia](https://en.wikipedia.org/wiki/A*_search_algorithm)
- [Disjoint-set / Union-Find — Wikipedia](https://en.wikipedia.org/wiki/Disjoint-set_data_structure)
- [ANSI escape codes — Wikipedia](https://en.wikipedia.org/wiki/ANSI_escape_code)
- [PEP 257 – Docstring Conventions](https://peps.python.org/pep-0257/)
- [mypy documentation](https://mypy.readthedocs.io/en/stable/)
- [flake8 documentation](https://flake8.pycqa.org/en/latest/)

### AI Usage

Claude (Anthropic) was used during this project for the following tasks:
- Reviewing algorithm correctness and edge case handling
- Generating this README and the code review document
- Explaining mypy strict mode errors

All AI-generated suggestions were reviewed, tested, and adapted by the team before inclusion.

---

## Team and Project Management

**Team members:** lciardo, lgreco

**Roles:**
- lciardo: Maze generation algorithms (generator.py), config parser (parser.py), settings editor (settings.py), Makefile and packaging (pyproject.toml)
- lgreco: Terminal display and rendering (display.py), solving algorithms (solver.py), output exporter (exporter.py), main application loop (a_maze_ing.py)

**Planning:**
The project was initially scoped to implement DFS generation only, then expanded to include Prim's and Kruskal's as bonus algorithms. The A* solver was added after the custom greedy solver was validated. The 42 pattern and color customization were integrated in the final phase.

**Tools used:** Python 3.10+, flake8, mypy, git, Claude (AI assistant for review)
