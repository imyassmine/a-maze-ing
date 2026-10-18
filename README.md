*This activity has been created as part of the 42 curriculum by yassabda and mdjigo.*

# A-Maze-ing

## Description
A-Maze-ing is a Python maze generator and viewer developed for the 42 curriculum. It reads a simple configuration file, generates a maze with a reproducible random seed, computes a shortest path between entry and exit, and can display the result in the terminal.

The project is split into small reusable modules:
- `mazegen.py` contains the core `Maze` / `MazeGenerator` and `Cell` classes — this is the standalone, pip-installable module.
- `src/config/parser.py` handles configuration loading and validation.
- `src/patterns/pattern42.py` adds the optional 42-shaped pattern.
- `src/ui/display.py` renders the maze in the terminal and handles user interactions.
- `writer.py` exports the maze to the output file format expected by the activity.

## Instructions
The project uses only the Python standard library at runtime (development tools: `flake8`, `mypy`, `pytest`, managed with `uv`).

### Run the project
```bash
make run
```

This command runs:
```bash
python3 a_maze_ing.py config.txt
```

### Debug
```bash
make debug
```

### Clean generated files
```bash
make clean
```

## Project Structure
```txt
a_maze_ing.py            # entry point, required at the repository root
mazegen.py               # standalone, pip-installable maze generator module
config.txt               # default configuration file
src/
  config/parser.py       # MazeConfig: configuration loading and validation
  patterns/pattern42.py  # optional "42" pattern
  ui/display.py          # terminal rendering and user interaction
tests/                   # pytest suite: configuration, generator, 42 pattern, output file
```

### Development commands
```bash
make install   # install dependencies with uv
make test      # run the test suite
make lint      # flake8 + mypy
make package   # build the mazegen wheel and sdist in dist/
```

## Configuration File
The configuration file is a plain text file made of `KEY=VALUE` pairs, one per line.
Comments can be added with `#`.

### Format
```txt
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
```

### Keys
- `WIDTH`: maze width in cells, positive integer.
- `HEIGHT`: maze height in cells, positive integer.
- `ENTRY`: entry cell coordinates as `x,y`.
- `EXIT`: exit cell coordinates as `x,y`.
- `OUTPUT_FILE`: path of the exported maze file.
- `PERFECT`: `True` or `False`. When `False`, the generator adds extra loops.
- `SEED`: optional integer seed. If omitted, a random 64-bit seed is used.

## Maze Generation Algorithm
The maze is generated with a recursive backtracking algorithm, also known as randomized depth-first search.
After the perfect maze is built, optional safe loop creation can break additional walls without creating invalid 3x3 open areas, so corridors never widen beyond the 2-cell limit required by the activity.

### Why this algorithm
- It is simple to implement and easy to validate.
- It guarantees that every cell is reachable in the perfect-maze case.
- It produces long corridors and a natural maze structure.
- It works well with deterministic seeding, so the same seed reproduces the same maze.

## Reusable Module
The reusable core of the project is the `MazeGenerator` class in `mazegen.py`.
It is a single, self-contained file with no dependency on the rest of the project, so it can be imported anywhere and is the file packaged for pip installation (`mazegen-*.whl` / `mazegen-*.tar.gz`).

### Basic example
```python
from mazegen import MazeGenerator

generator = MazeGenerator(width=20, height=15, seed=42)
generator.generate()

print(generator.grid[0][0].position)
print(generator.solution_directions)
```

### Custom parameters
Passed directly to the `MazeGenerator` constructor:
- `width`, `height`: size of the maze grid.
- `seed`: makes the generation reproducible.
- `entry`, `exit_pos`: coordinates used to compute the solution (default to `(0, 0)` and the bottom-right cell).
- `perfect`: when `False`, loops are added after the spanning maze is built.
- `loop_ratio`: how many safe extra walls may be removed when `perfect=False`.

### Accessing the generated structure
The generated structure is available through `generator.grid`.
Each cell exposes:
- `cell.position`: the `(x, y)` coordinates of the cell.
- `cell.walls`: a dictionary of walls for `North`, `East`, `South`, and `West`.
- `cell.visited`: the traversal state used during generation.

### Accessing a solution
- `generator.solution_directions`: shortest path from entry to exit as a list of directions, e.g. `['North', 'East', 'South', ...]`.
- `generator.solution_path`: the same path as a list of `(x, y)` coordinates.
- `generator.find_shortest_path(start, end)`: computes the shortest path between any two cells directly.
- `generator.export_output(path)`: writes the maze to the hexadecimal output file format described below.

## Display and Terminal Interaction
`src/ui/display.py` renders the maze as colored ASCII art in the terminal, showing walls, entry, exit, the optional 42 pattern, and (optionally) the solution path.

Once a maze is displayed, the following interactions are available:
- **Re-generate**: build and display a brand new maze from the same configuration.
- **Show/Hide path**: toggle highlighting of the shortest path between entry and exit.
- **Rotate colors**: switch between two color palettes for walls, entry, exit, and the 42 pattern.
- **Quit**: exit the program.

## Output File Format
The exported file written by `writer.py` contains:
1. One hexadecimal line per row of the maze grid.
2. A blank separator line.
3. The entry coordinates as `x,y`.
4. The exit coordinates as `x,y`.
5. The shortest path encoded with `N`, `E`, `S`, and `W`.

Example:
```txt
ABCDE
12345

0,0
19,14
EESSWN
```

## Team and Project Management
This project was completed as a two-person team (binôme): yassabda and mdjigo.

### Roles
- **yassabda**: maze generation logic (recursive backtracker), BFS shortest-path computation, configuration file parsing and validation, and the loop-adding / corridor-width constraints for non-perfect mazes.
- **mdjigo**: terminal display and user interaction, the 42 pattern logic, and the output file writer.
- Testing, documentation, and the README were shared between both members.

### Planning
The initial plan was to build a maze generator with a simple configuration file and a readable terminal output.
During development, the project evolved into a more modular codebase with separate files for generation, parsing, display, export, and the optional 42 pattern, plus a standalone `mazegen` module extracted for pip distribution.

### What worked well
- Splitting responsibilities into small, independently testable modules.
- Using a seed for reproducible results.
- Keeping the configuration format minimal and easy to edit.
- Dividing work along clear boundaries (generation/algorithms vs. display/output) reduced merge conflicts.

### What could be improved
- More automated tests for generation and export.
- Earlier agreement on the shared `Cell`/`Maze` interface, to avoid rework when extracting the reusable `mazegen` module.
- Resolving the SPDX license deprecation warning in `pyproject.toml` before submission.

### Tools Used
- Python standard library.
- `make` for common commands.
- `pdb` for debugging.
- `flake8` and `mypy` for code quality checks.
- Git for version control.

## Resources
- Python documentation: https://docs.python.org/3/
- `random` module: https://docs.python.org/3/library/random.html
- `collections.deque`: https://docs.python.org/3/library/collections.html#collections.deque
- Recursive backtracking maze generation: https://en.wikipedia.org/wiki/Maze_generation_algorithm
- Breadth-first search: https://en.wikipedia.org/wiki/Breadth-first_search

### AI Usage
AI was used to help draft and format this README, summarize the project structure, and organize the documentation sections required by the activity.
The implementation itself, naming choices, and code behavior were validated against the source files in this repository.