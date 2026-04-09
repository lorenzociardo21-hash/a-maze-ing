import sys

def config(namefile: str) -> dict[str, str]:

    dati_estratti: dict[str, str] = {}
    try:
        with open(namefile, 'r') as file_aperto:
            for riga_letta in file_aperto:
                riga_pulita = riga_letta.strip()
                if not riga_pulita:
                    continue
                if riga_pulita.startswith('#'):
                    continue
                if '=' in riga_pulita:
                    parti = riga_pulita.split('=', 1)
                    chiave = parti[0].strip().upper()
                    valore = parti[1].strip()
                    dati_estratti[chiave] = valore
                    
    except FileNotFoundError:
        print(f"Errore: Il file '{namefile}' non è stato trovato.")
        sys.exit(1)
    except Exception as e:
        print(f"Errore imprevisto durante la lettura del file: {e}")
        sys.exit(1)
    return dati_estratti


class mazeconfig:
    def __init__(self, dati_estratti: dict[str, str]) -> None:
        self.width: int = -1
        self.height: int = -1
        self.entry: tuple[int, int] = (-1, -1)
        self.exit: tuple[int, int] = (-1, -1)
        self.output_file: str = ""
        self.perfect = False

        try:
            self.width = int(dati_estratti["WIDTH"])
            self.height = int(dati_estratti["HEIGHT"])
            e_parti = dati_estratti["ENTRY"].split(",")
            self.entry = (int(e_parti[0]), int(e_parti[1]))
            x_parti = dati_estratti["EXIT"].split(",")
            self.exit = (int(x_parti[0]), int(x_parti[1]))
            self.output_file = dati_estratti["OUTPUT_FILE"]
            self.perfect = dati_estratti["PERFECT"] == "True"
            if self.entry[0] < 0 or self.entry[0] >= self.width or \
               self.entry[1] < 0 or self.entry[1] >= self.height:
                print("Errore: L'entrata è fuori dal labirinto!")
                sys.exit(1)
            if self.exit[0] < 0 or self.exit[0] > self.width or \
               self.exit[1] < 0 or self.exit[1] > self.height:
                print("Errore: L'uscita è fuori dal labirinto!")
                sys.exit(1)
            if self.entry == self.exit:
                print("Errore: Entrata e uscita non possono essere nello stesso posto!")
            if self.width <= 0 or self.height <= 0:
                print("Errore: Larghezza e altezza devono essere numeri positivi!")
                sys.exit(1)     
        except KeyError as e:
            print(f"Errore: Manca la chiave obbligatoria {e}")
            sys.exit(1)
        except ValueError:
            print("Errore: Hai scritto una parola dove volevo un numero!")
            sys.exit(1)
        except Exception as e:
            print(f"Errore: {e}")
            sys.exit(1)


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
        return [[15 for _ in range(self.width)] for _ in range(self.height)]
    
    def pattern42(self) -> set[tuple[int, int]]:
        center_x = self.width // 2 - 3
        center_y = self.height // 2 - 2
        return {(center_x + dx, center_y + dy) for dx, dy in PATTERN_42}

    def check_bounds(self, x: int, y: int):
        return 0 <= x < self.width and 0 <= y < self.height

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


def get_neighbours(grid: list[list[int]], x: int, y: int, visited: set) -> list[tuple[int, int, str]]:
    neighbours = []
    for direction, values in DIRECTIONS.items():
        if not grid[y][x] & values["num"]:
            nx, ny = x + values["dx"], y + values["dy"]
            if (nx, ny) not in visited:
                neighbours.append((nx, ny, direction))
    return neighbours


def maze_res(maze: MazeGenerator, grid: list[list[int]]) -> list[tuple[int, int, str]]:
    visited = set()
    stack = []
    current_x, current_y = maze.entry
    visited.add((current_x, current_y))

    while (current_x, current_y) != maze.exit:
        neighbours = get_neighbours(grid, current_x, current_y, visited)

        if neighbours:
            nx, ny, direction = neighbours[0]
            stack.append((current_x, current_y, direction))
            visited.add((nx, ny))
            current_x, current_y = nx, ny
        else:
            if not stack:
                return []
            current_x, current_y, _ = stack.pop()

    return stack

def crea_pezzi_cella(valore_cella: int, x: int, y: int, settings, percorso_coords: list[tuple[int, int]], risolvi: bool) -> tuple[str, str, str]:
    RESET = "\033[0m"
    MURO = "\033[95m" + "█" + RESET    
    VUOTO = "\033[96m" + "█" + RESET
    ENTRY = "\033[92m" + "█" + RESET
    EXIT = "\033[91m" + "█" + RESET
    QUARANTADUE = "\033[99m" + "█" + RESET
    PATH_COLOR = "\033[92m" + "█" + RESET
    if valore_cella == 15:
        MURO = QUARANTADUE
        VUOTO = QUARANTADUE

    sopra = MURO
    mezzo = ""
    sotto = MURO
    if valore_cella & 1: # il sopra
        sopra += MURO   # Chiudiamo il soffitto
    else:
        sopra += VUOTO  # Lasciamo un buco
    sopra += MURO       # Chiudiamo l'angolo destro
    # destra e sinistra  8 e 2
    if valore_cella & 8: # Muro a sinistra
        mezzo += MURO
    else:
        mezzo += VUOTO
    
    # Controllo per Entry, Exit e 42 e percorso
    if (x, y) == settings.entry:
        mezzo += ENTRY
    elif (x, y) == settings.exit:
        mezzo += EXIT
    elif valore_cella == 15: # Cella chiusa per il pattern 42
        mezzo += QUARANTADUE
    elif (x, y) in percorso_coords and risolvi:
        mezzo += PATH_COLOR
    else:
        mezzo += VUOTO 
        
    if valore_cella & 2: # Muro a destra
        mezzo += MURO
    else:
        mezzo += VUOTO
    # il sotto(4)
    if valore_cella & 4:
        sotto += MURO
    else:
        sotto += VUOTO
    sotto += MURO
    return sopra, mezzo, sotto

def disegna_maze(griglia: list[list[int]], settings, percorso, risolvi) -> None:
    percorso_coords = [(cella[0], cella[1]) for cella in percorso]
    print(percorso_coords)
    for y, riga_numeri in enumerate(griglia):
        linea_sopra = ""
        linea_mezzo = ""
        linea_sotto = ""
        for x, valore in enumerate(riga_numeri):
            p_sopra, p_mezzo, p_sotto = crea_pezzi_cella(valore, x, y, settings, percorso_coords, risolvi)
            linea_sopra += p_sopra
            linea_mezzo += p_mezzo
            linea_sotto += p_sotto
        print(linea_sopra)
        print(linea_mezzo)
        print(linea_sotto)

def main():
    settings = mazeconfig(config("config_prova.txt"))
    maze = MazeGenerator(settings)
    griglia = maze.generate_maze()
    print("--- LABIRINTO GENERATO ---")
    soluzione = maze_res(maze, griglia)
    disegna_maze(griglia, settings, soluzione, False)
    disegna_maze(griglia, settings, soluzione, True)


main()
