import random


DIRECTIONS = {
    "N": {"num": 1, "opposite": "S", "dx": 0, "dy": - 1},
    "S": {"num": 4, "opposite": "N", "dx": 0, "dy": 1},
    "E": {"num": 2, "opposite": "W", "dx": 1, "dy": 0},
    "W": {"num": 8, "opposite": "E", "dx": - 1, "dy": 0},
}


PATTERN_42 = [
    (0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 3), (2, 4), #4
    (4, 0), (5, 0), (6, 0), (6, 1), (6, 2), (5, 2), (4, 2), (4, 3), (4, 4), (5, 4), (6, 4), #2
]

class MazeGenerator:
    def __init__(self, maze) -> None:
        self.width: int = maze.width
        self.height: int = maze.height
        self.entry: tuple = maze.entry
        self.exit: tuple = maze.exit
        self.perfect: bool = maze.perfect

    def create_grid(self) -> list[list[int]]:
        '''ritorna una griglia piena di 15, quindi tutte mura'''
        return [[15 for _ in range(self.width + 1)] for _ in range(self.height + 1)]
    
    def pattern42(self) -> set[tuple[int, int]]:
        center_x = self.width // 2 - 3
        center_y = self.height // 2 - 2
        return {(center_x + dx, center_y + dy) for dx, dy in PATTERN_42}

    def check_bounds(self, x: int, y: int):
        return 0 <= x <= self.width and 0 <= y <= self.height

    def remove_wall(self, grid: list[list[int]],
                    x: int,
                    y: int, direction: str) -> None:
        '''rimuove i muri rifacendosi al dizionario, dove e' presente la direzione, l'opposto e il numero con cui confrontare'''
        neighbour_x = x + DIRECTIONS[direction]["dx"]
        neighbour_y = y + DIRECTIONS[direction]["dy"]
        opposite = DIRECTIONS[direction]["opposite"]

        grid[y][x] &= ~DIRECTIONS[direction]["num"] #using the bitwise operators cause it's less prone to cause errors, the & is the "and" operator and the ~ is the not operator
        grid[neighbour_y][neighbour_x] &= ~DIRECTIONS[opposite]["num"]

    def square_3x3(self, grid: list[list[int]], nx: int, ny: int, visited: set=None) -> bool:
        if visited is None:
            visited = set()
        '''Guarda se nei dinteorni della cella si forma un quadrato 3x3, controlla tutta la zona usando una flag square3x3'''
        for block_x in range(nx - 2, nx + 1):
            for block_y in range(ny - 2, ny + 1):
                square3x3 = True
                for dx in range(3):
                    for dy in range(3):
                        cell_x, cell_y = block_x + dx, block_y + dy
                        if (not self.check_bounds(cell_x, cell_y)) or (grid[cell_y][cell_x] == 15 and (cell_x, cell_y) not in visited):
                            square3x3 = False
                            break
                    if not square3x3:
                        break
                if square3x3:
                    return True
        return False

    def unvisited_neighbours(self, x: int, y: int, pattern_cells: set, visited: set) -> list[tuple[int, int, str]]:
        '''Guarda le celle nei dintorni della cella corrente paasatagli e rende una lista di esse,
        le quali non sono gia state visitate o non sono nel pattern42'''
        neighbours = []
        for direction, values in DIRECTIONS.items():
            neighbour_x, neighbour_y = x + values["dx"], y + values["dy"]
            if (self.check_bounds(neighbour_x, neighbour_y)
                and (neighbour_x, neighbour_y) not in visited
                and (neighbour_x, neighbour_y) not in pattern_cells):
                neighbours.append((neighbour_x, neighbour_y, direction))
        return neighbours

    def can_show_pattern(self) -> bool:
        return self.width >= 10 and self.height >= 7

    def get_remaining_walls(self, grid: list[list[int]], pattern_cells: set, percentage: float = 0.15) -> list[tuple]:
        '''viene usata per il non perfect maze, rende una lista celle, che hanno dei muri, randomica e secondo una percentuale k,
        guarda solo se la cella ha muri ad est o sud, perche si muove da sinistra a destra e dall'alto verso il basso. Oltre ai classici controlli dei limiti e delle celle 42'''
        walls = []
        for row in range(self.height):
            for column in range(self.width):
                if (column, row) not in pattern_cells:
                    if (grid[row][column] & 2 and self.check_bounds(column + 1, row)
                    and (column + 1, row) not in pattern_cells):
                        walls.append((column, row, "E"))
                    if (grid[row][column] & 4 and self.check_bounds(column, row + 1)
                    and (column, row + 1) not in pattern_cells):
                        walls.append((column, row, "S"))
        if not 0 <= percentage <= 1:
            raise ValueError("Percentage must be between 0 and 1.")
        k = int(len(walls) * percentage)
        return random.sample(walls, k)

    def generate_maze(self, seed: int = None) -> list[list[int]]:
        '''genera il maze, sia con perfect che non, utilizza DFS, avendo una lista di visitati formata da tuple di coordinate
        e poi ha uno variabile stack dalla quale toglie la cella solo se non ha celle vicine, quindi non visitate, fuori dai limiti e celle del pattern'''

        random.seed(seed)
        grid = self.create_grid()
        pattern_cells = set()
        if self.can_show_pattern():
            pattern_cells = self.pattern42()
        visited = set()
        visited.add(self.entry)
        stack = [self.entry]

        while stack:
            x, y = stack[-1]
            neighbours = self.unvisited_neighbours(x, y, pattern_cells, visited)
            neighbours = [
                (nx, ny, direction) for nx, ny, direction in neighbours
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
            chosen_ones = self.get_remaining_walls(grid, pattern_cells, 0.15)
            while chosen_ones:
                x, y, d = chosen_ones[-1]
                self.remove_wall(grid, x, y, d)
                chosen_ones.pop()

        return grid
