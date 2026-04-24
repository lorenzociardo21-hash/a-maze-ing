import sys
import random
from src.parser import mazeconfig
from typing import TypedDict


class DirectionInfo(TypedDict):
    num: int
    opposite: str
    dx: int
    dy: int


DIRECTIONS: dict[str, DirectionInfo] = {
    "N": {"num": 1, "opposite": "S", "dx": 0, "dy": -1},
    "S": {"num": 4, "opposite": "N", "dx": 0, "dy": 1},
    "E": {"num": 2, "opposite": "W", "dx": 1, "dy": 0},
    "W": {"num": 8, "opposite": "E", "dx": -1, "dy": 0},
}


class MazeGenerator:
    """Gestisce la generazione della struttura del labirinto."""
    def __init__(self, maze: mazeconfig) -> None:
        self.width: int = maze.width
        self.height: int = maze.height
        self.entry: tuple[int, int] = maze.entry
        self.exit: tuple[int, int] = maze.exit
        self.perfect: bool = maze.perfect
        self.seed: str | None = maze.seed
        self.pattern_cells: set[tuple[int, int]] = maze.pattern_cells

    def create_grid(self) -> list[list[int]]:
        '''ritorna una griglia piena di 15, quindi tutte mura'''
        return [[15 for _ in range(self.width + 1)]
                for _ in range(self.height + 1)]

    def check_bounds(self, x: int, y: int) -> bool:
        """Verifica che la cella sia dentro i limiti."""
        return 0 <= x <= self.width and 0 <= y <= self.height

    def remove_wall(self, grid: list[list[int]],
                    x: int,
                    y: int, direction: str) -> None:
        '''rimuove i muri rifacendosi al dizionario, dove e'
        presente la direzione, l'opposto e il numero con cui confrontare'''
        a: int = DIRECTIONS[direction]["dx"]
        b: int = DIRECTIONS[direction]["dy"]
        neighbour_x = x + a
        neighbour_y = y + b
        opposite = DIRECTIONS[direction]["opposite"]

        grid[y][x] &= ~DIRECTIONS[direction]["num"]
        grid[neighbour_y][neighbour_x] &= ~DIRECTIONS[opposite]["num"]

    def square_3x3(self, grid: list[list[int]], nx: int,
                   ny: int,
                   visited: set[tuple[int, int]] | None = None) -> bool:
        if visited is None:
            visited = set()
        '''Guarda se nei dinteorni della cella si forma un quadrato 3x3,
        controlla tutta la zona usando una flag square3x3'''
        for block_x in range(nx - 2, nx + 1):
            for block_y in range(ny - 2, ny + 1):
                square3x3 = True
                for dx in range(3):
                    for dy in range(3):
                        cell_x, cell_y = block_x + dx, block_y + dy
                        if ((not self.check_bounds(cell_x, cell_y)) or
                            (grid[cell_y][cell_x] == 15 and
                             (cell_x, cell_y) not in visited)):
                            square3x3 = False
                            break
                    if not square3x3:
                        break
                if square3x3:
                    return True
        return False

    def unvisited_neighbours(self, x: int, y: int,
                             pattern_cells: set[tuple[int, int]],
                             visited: set[tuple[int, int]]) -> list[tuple
                                                                    [int,
                                                                     int,
                                                                     str]]:
        '''Guarda le celle nei dintorni della cella
        corrente paasatagli e rende una lista di esse,
        le quali non sono gia state visitate o non sono nel pattern42'''
        neighbours: list[tuple[int, int, str]] = []
        for direction, values in DIRECTIONS.items():
            neighbour_x, neighbour_y = x + values["dx"], y + values["dy"]
            if (self.check_bounds(neighbour_x, neighbour_y) and
                ((neighbour_x, neighbour_y) not in visited
                 and (neighbour_x, neighbour_y) not in pattern_cells)):
                neighbours.append((neighbour_x, neighbour_y, direction))
        return neighbours

    def get_remaining_walls(self, grid: list[list[int]],
                            pattern_cells: set[tuple[int, int]],
                            percentage: float = 0.15) -> list[tuple[int,
                                                                    int,
                                                                    str]]:
        '''viene usata per il non perfect maze, rende una lista celle,
        che hanno dei muri, randomica e secondo una percentuale k,
        guarda solo se la cella ha muri ad est o sud, perche si muove
        da sinistra a destra e dall'alto verso il basso. Oltre ai classici
        controlli dei limiti e delle celle 42'''
        walls: list[tuple[int, int, str]] = []
        for row in range(self.height):
            for column in range(self.width):
                if (column, row) not in pattern_cells:
                    if (grid[row][column] & 2 and
                        (self.check_bounds(column + 1, row)
                         and (column + 1, row) not in pattern_cells)):
                        walls.append((column, row, "E"))
                    if (grid[row][column] & 4 and
                        (self.check_bounds(column, row + 1)
                         and (column, row + 1) not in pattern_cells)):
                        walls.append((column, row, "S"))
        if not 0 <= percentage <= 1:
            raise ValueError("Percentage must be between 0 and 1.")
        k = int(len(walls) * percentage)
        return random.sample(walls, k)

    def wall_to_list(self, x: int, y: int,
                     wall_list: list[tuple[int, int, int, int, str]],
                     visited: set[tuple[int, int]],
                     pattern_cells: set[tuple[int, int]]) -> None:
        '''prende tutti i muri nella griglia '''
        for d, val in DIRECTIONS.items():
            nx, ny = x + val["dx"], y + val["dy"]
            if (self.check_bounds(nx, ny) and
                ((nx, ny) not in visited
                 and (nx, ny) not in pattern_cells)):
                wall_list.append((x, y, nx, ny, d))

    def generate_maze_prims(self) -> tuple[list[list[int]], int]:
        ''' algorimo prim'''
        seed_val: int
        try:
            seed_val = int(self.seed)  # type: ignore[arg-type]
        except ValueError:
            if self.seed == "None":
                seed_val = random.randrange(sys.maxsize)
            else:
                print("Il seed non e' un numero! Ciao")
                sys.exit(1)
        if seed_val < 0:
            print("Errore: il seed non deve essere negativo!")
            sys.exit(1)
        random.seed(seed_val)
        grid = self.create_grid()
        visited: set[tuple[int, int]] = {(self.entry[0], self.entry[1])}
        walls: list[tuple[int, int, int, int, str]] = []
        self.wall_to_list(self.entry[0], self.entry[1],
                          walls, visited, self.pattern_cells)

        while walls:
            wall_idx = random.randint(0, len(walls) - 1)
            c1_x, c1_y, c2_x, c2_y, direction = walls.pop(wall_idx)
            if (c2_x, c2_y) not in visited:
                if not self.square_3x3(grid, c2_x, c2_y, visited):
                    self.remove_wall(grid, c1_x, c1_y, direction)
                    visited.add((c2_x, c2_y))
                    self.wall_to_list(c2_x, c2_y, walls,
                                      visited, self.pattern_cells)

        if not self.perfect:
            chosen_ones = self.get_remaining_walls(grid,
                                                   self.pattern_cells, 0.15)
            while chosen_ones:
                x, y, d = chosen_ones[-1]
                self.remove_wall(grid, x, y, d)
                chosen_ones.pop()

        return grid, seed_val

    def find(self, cell: tuple[int, int],
             parent: dict[tuple[int, int],
                          tuple[int, int]]) -> tuple[int, int]:
        ''' cerca le celle che non sono nello stesso set'''
        root = cell
        while parent[root] != root:
            root = parent[root]
        curr = cell
        while parent[curr] != root:
            n_node = parent[curr]
            parent[curr] = root
            curr = n_node
        return root

    def union(self, cell1: tuple[int, int], cell2: tuple[int, int],
              parent: dict[tuple[int, int], tuple[int, int]]) -> bool:
        ''' unisce le celle nello stesso set'''
        root1 = self.find(cell1, parent)
        root2 = self.find(cell2, parent)
        if root1 != root2:
            parent[root1] = root2
            return True
        return False

    def generate_maze_kruskal(self) -> tuple[list[list[int]], int]:
        ''' kruskal's algorithm '''
        seed_val: int
        try:
            seed_val = int(self.seed)  # type: ignore[arg-type]
        except ValueError:
            if self.seed == "None":
                seed_val = random.randrange(sys.maxsize)
            else:
                print("Il seed non e' un numero! Ciao")
                sys.exit(1)
        if seed_val < 0:
            print("Errore: il seed non deve essere negativo!")
            sys.exit(1)
        random.seed(seed_val)
        grid = self.create_grid()
        parent: dict[tuple[int, int], tuple[int, int]] = {
            (x, y): (x, y) for y in range(self.height + 1)
            for x in range(self.width + 1)
            if (x, y) not in self.pattern_cells
        }
        walls: list[tuple[int, int, int, int, str]] = []
        for y in range(self.height + 1):
            for x in range(self.width + 1):
                if (x, y) in self.pattern_cells:
                    continue
                for d in ["E", "S"]:
                    nx, ny = x + DIRECTIONS[d]["dx"], y + DIRECTIONS[d]["dy"]
                    if ((self.check_bounds(nx, ny)
                         and (nx, ny) not in self.pattern_cells)):
                        walls.append((x, y, nx, ny, d))

        random.shuffle(walls)
        for x1, y1, x2, y2, d in walls:
            if self.find((x1, y1), parent) != self.find((x2, y2), parent):
                self.union((x1, y1), (x2, y2), parent)
                self.remove_wall(grid, x1, y1, d)

        if not self.perfect:
            chosen_ones = self.get_remaining_walls(grid,
                                                   self.pattern_cells, 0.15)
            while chosen_ones:
                x, y, d = chosen_ones[-1]
                self.remove_wall(grid, x, y, d)
                chosen_ones.pop()

        return grid, seed_val

    def generate_maze_dfs(self) -> tuple[list[list[int]], int]:
        '''genera il maze, sia con perfect che non, utilizza DFS,
        avendo una lista di visitati formata da tuple di coordinate
        e poi ha uno variabile stack dalla quale toglie la cella solo
        se non ha celle vicine, quindi non visitate, fuori dai limiti
        e celle del pattern'''
        seed_val: int
        try:
            seed_val = int(self.seed)  # type: ignore[arg-type]
        except ValueError:
            if self.seed == "None":
                seed_val = random.randrange(sys.maxsize)
            else:
                print("Il seed non e' un numero! Ciao")
                sys.exit(1)
        if seed_val < 0:
            print("Errore: il seed non deve essere negativo!")
            sys.exit(1)
        random.seed(seed_val)
        grid = self.create_grid()
        visited: set[tuple[int, int]] = set()
        visited.add(self.entry)
        stack: list[tuple[int, int]] = [self.entry]

        while stack:
            x, y = stack[-1]
            neighbours = [
                (nx, ny, direction)
                for nx, ny, direction
                in self.unvisited_neighbours(x, y, self.pattern_cells, visited)
                if not self.square_3x3(grid, nx, ny, visited)
            ]

            if neighbours:
                nx, ny, d = random.choice(neighbours)
                self.remove_wall(grid, x, y, d)
                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()
        if not self.perfect:
            chosen_ones = self.get_remaining_walls(grid,
                                                   self.pattern_cells, 0.15)
            while chosen_ones:
                x, y, d = chosen_ones[-1]
                self.remove_wall(grid, x, y, d)
                chosen_ones.pop()

        return grid, seed_val
