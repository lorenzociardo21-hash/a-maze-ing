import sys, time

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
        self.seed = None

        try:
            self.width = int(dati_estratti["WIDTH"])
            self.height = int(dati_estratti["HEIGHT"])
            e_parti = dati_estratti["ENTRY"].split(",")
            self.entry = (int(e_parti[0]), int(e_parti[1]))
            x_parti = dati_estratti["EXIT"].split(",")
            self.exit = (int(x_parti[0]), int(x_parti[1]))
            self.output_file = dati_estratti["OUTPUT_FILE"]
            self.perfect = dati_estratti["PERFECT"] == "True"
            self.seed = dati_estratti["SEED"]
            if self.entry[0] < 0 or self.entry[0] > self.width or \
               self.entry[1] < 0 or self.entry[1] > self.height:
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
        self.seed: str = maze.seed

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

    def wall_to_list(self, x: int, y: int, wall_list: list[tuple[int, int, int, int, str]], visited: set, pattern_cells: set) -> None:
        for d, val in DIRECTIONS.items():
            nx, ny = x + val["dx"], y + val["dy"]
            if self.check_bounds(nx, ny) and (nx, ny) not in visited and (nx, ny) not in pattern_cells:
                wall_list.append((x, y, nx, ny, d))

    def generate_maze_prims(self) -> list[list[int]]:
        try:
            seed = int(self.seed)
        except ValueError:
            if self.seed == "None":
                seed = random.randrange(sys.maxsize)
            else:
                print("Il seed non e' un numero! Ciao")
                sys.exit(1)
        if seed < 0:
            print("Errore: il seed non deve essere negativo!")
            sys.exit(1)
        random.seed(seed)
        grid = self.create_grid()
        pattern_cells = set()
        if self.can_show_pattern():
            pattern_cells = self.pattern42()
        if self.entry in pattern_cells or self.exit in pattern_cells:
            print("Errore: L'entrata o l'uscita cadono dentro il pattern 42!")
            sys.exit(1)
        visited = {(self.entry[0], self.entry[1])}
        walls = []
        self.wall_to_list(self.entry[0], self.entry[1], walls, visited, pattern_cells)

        while walls:
            wall_idx = random.randint(0, len(walls) - 1)
            c1_x, c1_y, c2_x, c2_y, direction = walls.pop(wall_idx)
            if (c2_x, c2_y) not in visited:
                if not self.square_3x3(grid, c2_x, c2_y, visited):
                    self.remove_wall(grid, c1_x, c1_y, direction)
                    visited.add((c2_x, c2_y))
                    self.wall_to_list(c2_x, c2_y, walls, visited, pattern_cells)

        if not self.perfect:
            chosen_ones = self.get_remaining_walls(grid, pattern_cells, 0.15)
            while chosen_ones:
                x, y, d = chosen_ones[-1]
                self.remove_wall(grid, x, y, d)
                chosen_ones.pop()

        return grid, seed

    def find(self, cell: tuple, parent: dict) -> tuple:
        root = cell
        while parent[root] != root:
            root = parent[root]
        curr = cell
        while parent[curr] != root:
            n_node = parent[curr]
            parent[curr] = root
            curr = n_node
        return root

    def union(self, cell1: tuple, cell2: tuple, parent: dict) -> bool:
        root1 = self.find(cell1, parent)
        root2 = self.find(cell2, parent)
        if root1 != root2:
            parent[root1] = root2
            return True
        return False

    def generate_maze_kruskal(self) -> list[list[int]]:
        try:
            seed = int(self.seed)
        except ValueError:
            if self.seed == "None":
                seed = random.randrange(sys.maxsize)
            else:
                print("Il seed non e' un numero! Ciao")
                sys.exit(1)
        if seed < 0:
            print("Errore: il seed non deve essere negativo!")
            sys.exit(1)
        random.seed(seed)
        grid = self.create_grid()
        pattern_cells = set()
        if self.can_show_pattern():
            pattern_cells = self.pattern42()
        if self.entry in pattern_cells or self.exit in pattern_cells:
            print("Errore: L'entrata o l'uscita cadono dentro il pattern 42!")
            sys.exit(1)
        parent = {(x, y): (x, y) for y in range(self.height + 1) for x in range(self.width + 1) if (x, y) not in pattern_cells}
        walls = []
        for y in range(self.height + 1):
            for x in range(self.width + 1):
                if (x, y) in pattern_cells:
                    continue
                for d in ["E", "S"]:
                    nx, ny = x + DIRECTIONS[d]["dx"], y + DIRECTIONS[d]["dy"]
                    if self.check_bounds(nx, ny) and (nx, ny) not in pattern_cells:
                        walls.append((x, y, nx, ny, d))

        random.shuffle(walls)
        for x1, y1, x2, y2, d in walls:
            if self.find((x1, y1), parent) != self.find((x2, y2), parent):
                self.union((x1, y1), (x2, y2), parent)
                self.remove_wall(grid, x1, y1, d)

        if not self.perfect:
            chosen_ones = self.get_remaining_walls(grid, pattern_cells, 0.15)
            while chosen_ones:
                x, y, d = chosen_ones[-1]
                self.remove_wall(grid, x, y, d)
                chosen_ones.pop()

        return grid, seed

    def generate_maze(self) -> list[list[int]]:
        '''genera il maze, sia con perfect che non, utilizza DFS, avendo una lista di visitati formata da tuple di coordinate
        e poi ha uno variabile stack dalla quale toglie la cella solo se non ha celle vicine, quindi non visitate, fuori dai limiti e celle del pattern'''
        try:
            seed = int(self.seed)
        except ValueError:
            if self.seed == "None":
                seed = random.randrange(sys.maxsize)
            else:
                print("Il seed non e' un numero! Ciao")
                sys.exit(1)
        if seed < 0:
            print("Errore: il seed non deve essere negativo!")
            sys.exit(1)
        random.seed(seed)
        grid = self.create_grid()
        pattern_cells = set()
        if self.can_show_pattern():
            pattern_cells = self.pattern42()
        if self.entry in pattern_cells or self.exit in pattern_cells:
            print("Errore: L'entrata o l'uscita cadono dentro il pattern 42!")
            sys.exit(1)
        visited = set()
        visited.add(self.entry)
        stack = [self.entry]

        while stack:
            x, y = stack[-1]
            neighbours = [
                (nx, ny, direction) for nx, ny, direction in self.unvisited_neighbours(x, y, pattern_cells, visited)
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

        return grid, seed


def get_neighbours(grid: list[list[int]], x: int, y: int, visited: set) -> list[tuple[int, int, str]]:
    neighbours = []
    for direction, values in DIRECTIONS.items():
        if not grid[y][x] & values["num"]:
            nx, ny = x + values["dx"], y + values["dy"]
            if (nx, ny) not in visited:
                neighbours.append((nx, ny, direction))
    return neighbours


def distance(x1: int, y1: int, exit: tuple[int, int]) -> int:
    return ((exit[0] - x1)**2 + (exit[1] - y1) **2)**0.5


def find_dir(grid: list[list[int]], x: int, y: int, exit: tuple[int, int], visited: set) -> tuple[int, int, str]:
    min_dist = 2**32
    min_x, min_y = x, y
    direction = None
    for direc, values in DIRECTIONS.items():
        if not grid[y][x] & values["num"]:
            dx, dy = x + values["dx"], y + values["dy"]
            if (dx, dy) not in visited:
                d = distance(dx, dy, exit)
                if d < min_dist:
                    min_dist, min_x, min_y, direction = d, dx, dy, direc
    return min_dist, min_x, min_y, direction


def check_stack(grid: list[list[int]], stack: list[tuple[int, int, str]]) -> None:
    changed = True
    while changed:
        changed = False
        pos_index = {(x, y): i for i, (x, y, _) in enumerate(stack)}
        for i, (x, y, _) in enumerate(stack):
            for direc, val in DIRECTIONS.items():
                dx, dy = x + val["dx"], y + val["dy"]
                if (dx, dy) in pos_index:
                    j = pos_index[(dx, dy)]
                    if j > i + 1 and not grid[y][x] & val["num"]:
                        stack = stack[:i + 1] + stack[j:]
                        stack[i] = (x, y, direc)
                        changed = True
                        break
            if changed:
                break
    return stack


def check_distance(grid: list[list[int]], neighbours: list[tuple[int, int, str]], exit: tuple[int, int], visited: set) -> tuple[int, int, str]:
    min_x, min_y, direction_min = neighbours[0]
    min_ndist, _, _, _ = find_dir(grid, min_x, min_y, exit, visited | {(min_x, min_y)})
    if (min_x, min_y) == exit:
        return min_x, min_y, direction_min
    for x, y, direction in neighbours[1:]:
        if distance(x, y, exit) < distance(min_x, min_y, exit) or (x, y) == exit:
            next_dist, nx, ny, _ = find_dir(grid, x, y, exit, visited | {(x, y)})
            if next_dist < min_ndist or (nx, ny) == exit or (x, y) == exit:
                min_x, min_y, direction_min = x, y, direction
                min_ndist = next_dist
    return min_x, min_y, direction_min


def maze_res_astar(maze: MazeGenerator, grid: list[list[int]]) -> list[tuple[int, int, str]]:
    start = maze.entry
    exit = maze.exit
    stack = [(distance(*start, exit), 0, start[0], start[1])]
    came_from = {start: None}
    steps_made = {start: 0}
    while stack:
        _, steps, x, y = stack.pop()
        if (x, y) == exit:
            path = []
            current = (x, y)
            while came_from[current] is not None:
                prev, direction = came_from[current]
                path.append((prev[0], prev[1], direction))
                current = prev
            path.reverse()
            path.append((exit[0], exit[1], None))
            return path
        for nx, ny, direction in get_neighbours(grid, x, y, came_from):
            new_step = steps + 1
            if (nx, ny) not in steps_made or new_step < steps_made[(nx, ny)]:
                steps_made[(nx, ny)] = new_step
                a_score = new_step + distance(nx, ny, exit)
                stack.append((a_score, new_step, nx, ny))
                stack = sorted(stack, key=lambda x: x[0], reverse=True)
                came_from[(nx, ny)] = ((x, y), direction)
    return []


def maze_res_mix_algo(maze: MazeGenerator, grid: list[list[int]]) -> list[tuple[int, int, str]]:
    visited = set()
    stack = []
    current_x, current_y = maze.entry
    visited.add((current_x, current_y))

    while (current_x, current_y) != maze.exit:
        neighbours = get_neighbours(grid, current_x, current_y, visited)

        if neighbours:
            nx, ny, direction = check_distance(grid, neighbours, maze.exit, visited)
            stack.append((current_x, current_y, direction))
            visited.add((nx, ny))
            current_x, current_y = nx, ny
        else:
            if not stack:
                return []
            current_x, current_y, _ = stack.pop()

    stack.append((maze.exit[0], maze.exit[1], None))
    stack = check_stack(grid, stack)

    return stack


def crea_pezzi_cella(valore_cella: int, x: int, y: int, settings: mazeconfig, percorso_coords: list[tuple[int, int]], risolvi: bool, colore: str) -> tuple[str, str, str]:
    RESET = "\033[0m"
    MURO = colore[0] + "██" + RESET
    VUOTO = colore[1] + "██" + RESET
    ENTRY = "\033[92m" + "██" + RESET
    EXIT = "\033[91m" + "██" + RESET
    QUARANTADUE = colore[2]+ "██" + RESET
    PATH_COLOR = "\033[92m" + "██" + RESET
    if valore_cella == 15:
        MURO = QUARANTADUE
        VUOTO = QUARANTADUE

    sopra = MURO
    mezzo = ""
    sotto = MURO

    if valore_cella & 1: # il sopra
        sopra += MURO   # Chiudiamo il soffitto
    elif (x, y - 1) in percorso_coords and risolvi and (x, y) in percorso_coords:
        sopra += PATH_COLOR
    else:
        sopra += VUOTO  # Lasciamo un buco
    sopra += MURO       # Chiudiamo l'angolo destro

    if valore_cella & 8: # Muro a sinistra
        mezzo += MURO
    elif (x - 1, y) in percorso_coords and risolvi and (x, y) in percorso_coords:
        mezzo += PATH_COLOR
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
    elif (x + 1, y) in percorso_coords and risolvi and (x, y) in percorso_coords:
        mezzo += PATH_COLOR
    else:
        mezzo += VUOTO
    # il sotto(4)
    if valore_cella & 4:
        sotto += MURO
    elif (x, y + 1) in percorso_coords and risolvi and (x, y) in percorso_coords:
        sotto += PATH_COLOR
    else:
        sotto += VUOTO
    sotto += MURO
    return sopra, mezzo, sotto


def sceltacolore(scelta_utente: int, colori_attuali: list[str]) -> list[str]:
    palette = [
        "\033[95m", "\033[96m", "\033[97m", "\033[93m", "\033[94m", "\033[91m",
        "\033[92m", "\033[90m", "\033[31m", "\033[32m", "\033[33m", "\033[34m",
        "\033[35m", "\033[36m"
    ]

    if scelta_utente in [1, 2, 3]:
        idx_da_cambiare = scelta_utente - 1
        colore_vecchio = colori_attuali[idx_da_cambiare]
        try:
            indice_palette = palette.index(colore_vecchio)
        except ValueError:
            indice_palette = 0
            
        trovato = False
        while not trovato:
            indice_palette = (indice_palette + 1) % len(palette)
            nuovo_colore = palette[indice_palette]
            if nuovo_colore not in colori_attuali:
                trovato = True
                
        colori_attuali[idx_da_cambiare] = nuovo_colore
        return colori_attuali

    elif scelta_utente == 4:
        nuovicolori = []
        for _ in colori_attuali:
            trovato = False
            while not trovato:
                indice_p = random.randint(0, len(palette) - 1)
                colore_pescato = palette[indice_p]
                if colore_pescato not in nuovicolori:
                    nuovicolori.append(colore_pescato)
                    trovato = True
        return nuovicolori
    return colori_attuali


def printamazing() -> None:
        title = r"""
        █████           ███    ███   █████  ███████ ███████          ██  ███    ██   ██████ 
        ██   ██          ████  ████  ██   ██    ███  ██               ██  ████   ██  ██      
        ███████   ███    ██ ████ ██  ███████   ███   █████     ███    ██  ██ ██  ██  ██   ███
        ██   ██          ██  ██  ██  ██   ██  ███    ██               ██  ██  ██ ██  ██    ██
        ██   ██          ██      ██  ██   ██ ███████ ███████          ██  ██   ████   ██████ 
        """
        print(title)

def disegna_maze(griglia: list[list[int]], settings: mazeconfig, percorso: list[tuple[int, int, str]], risolvi: bool, colore: str) -> None:
    percorso_coords = []
    for cella in percorso:
        nuova_coppia = (cella[0], cella[1])
        percorso_coords.append(nuova_coppia)
    i = 0
    percorsofinito = []
    if risolvi:
        while i < len(percorso):
            print("\033[2J\033[H\033[3J", end="")
            printamazing()
            percorsofinito.append(percorso_coords[i]) 
            for y, riga_numeri in enumerate(griglia):
                linea_sopra = ""
                linea_mezzo = ""
                linea_sotto = ""
                for x, valore in enumerate(riga_numeri):
                    p_sopra, p_mezzo, p_sotto = crea_pezzi_cella(valore, x, y, settings, percorsofinito, risolvi, colore)
                    linea_sopra += p_sopra
                    linea_mezzo += p_mezzo
                    linea_sotto += p_sotto
                print(linea_sopra)
                print(linea_mezzo)
                print(linea_sotto)
            i += 1
            time.sleep(0.1)
        
    else:
        printamazing()
        for y, riga_numeri in enumerate(griglia):
            linea_sopra = ""
            linea_mezzo = ""
            linea_sotto = ""
            for x, valore in enumerate(riga_numeri):
                p_sopra, p_mezzo, p_sotto = crea_pezzi_cella(valore, x, y, settings, percorso_coords, risolvi, colore)
                linea_sopra += p_sopra
                linea_mezzo += p_mezzo
                linea_sotto += p_sotto
            print(linea_sopra)
            print(linea_mezzo)
            print(linea_sotto)

        
def output(griglia, soluzione, settings):
    esadecimale = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"]
    with open(settings.output_file, "w") as f:
        for riga in griglia:
            for valore in riga:
                f.write(esadecimale[valore])
            f.write("\n")
        f.write(f"\n{settings.entry[0]},{settings.entry[1]}\n")
        f.write(f"{settings.exit[0]},{settings.exit[1]}\n")
        for valore in soluzione:
            if valore[2] is not None:
                f.write(valore[2])
        f.write("\n")
        
    



def main() -> None:
    if len(sys.argv) != 2:
        print("Errore: Numero di argomenti sbagliato.")
        print("Usare: python3 a_maze_ing.py <config_file>")
        sys.exit(1)
    settings = mazeconfig(config(sys.argv[1]))
    maze = MazeGenerator(settings)
    indicealg = 0
    listaalg = [maze.generate_maze_kruskal, maze.generate_maze_prims, maze.generate_maze]
    griglia, seed = listaalg[indicealg]()
    soluzione = maze_res_mix_algo(maze, griglia)
    output(griglia, soluzione, settings)
    colore = ["\033[95m", "\033[97m", "\033[93m"]
    risolvi = False
    printamazing()
    try:
        while True:
            print("\033[2J\033[H\033[3J", end="")
            disegna_maze(griglia, settings, soluzione, risolvi, colore)
            print("\n\033[91m1. Generare nuovo labirinto\033[0m")
            print("\033[95m2. Mostrate percorso\033[0m")
            print("\033[97m3. Cambiare colore\033[0m")
            print("\033[97m4. Cambia algoritmo\033[0m")
            print("\033[97m5. Vuoi il seed????\033[0m")
            print("\033[97m6. Scegli le TUE impostazioni!\033[0m")
            print("\033[93m7. Uscire\033[0m")
            scelta = input("\nscegliiiiii: ")
            if scelta == "1":
                if settings.seed is not "None":
                    print("Non puoi generarlooo! hai impostato il seed!\nMetti il seed a None!!!")
                    time.sleep(4)
                griglia, seed = listaalg[indicealg]()
                soluzione = maze_res_mix_algo(maze, griglia)
                output(griglia, soluzione, settings)
            elif scelta == "2":
                risolvi = not risolvi
            elif scelta == "3":
                    risolvi = False
                    print("1. Muri | 2. Corridoio | 3. 42 | 4. Scelta pazzerella")
                    quale = input("Quale parte vuoi cambiare? ")
                    if quale in ["1", "2", "3", "4"]:
                        colore= sceltacolore(int(quale), colore)
            elif scelta == "4":
                print("1. Kruskal | 2. Prims | 3. DFS")
                alg = input("Scegli un algoritmo!!! ")
                if alg in ["1", "2", "3"]:
                    indicealg = int(alg) - 1
            elif scelta == "5":
                input(f"Eccolooooo:\n{seed}\n\nPremi qualcoa e invio per continuare!")
            elif scelta == "6":
                print(f"\033[97m1. WDTH:{settings.width}\033[0m")
                print(f"\033[97m2. HEIGHT:{settings.height}\033[0m")
                print(f"\033[97m3. ENTRY:{settings.entry}\033[0m")
                print(f"\033[97m5. EXIT:{settings.exit}\033[0m")
                print(f"\033[97m4. OUTPUT_FILE Name:{settings.output_file}\033[0m")
                print(f"\033[97m5. PERFECT:{settings.perfect}\033[0m")
                print(f"\033[97m6. SEED:{settings.seed}\033[0m")
                sceltaimp= input("\nscegli quello che vuoi cambiare!!")
                if sceltaimp in ["1", "2", "3", "4", "5", "6"]:
                    impostazioni = ["WDTH=", "HEIGHT=", "ENTRY=", "EXIT=",
                                    "OUTPUT_FILE=", "PERFECT=", "SEED="]
                    nuovo_valore = impostazioni[int(sceltaimp) - 1] + input("Cambia il valore!")
                    change_config(sys.argv[1], nuovo_valore, settings)
                    if change_config == 0:
                        main()
                    else:
                        print("hai sbagliato a scriverleee!!")
                        time.sleep(4)

            elif scelta == "7":
                print("Ciaoooo")
                break
    except (KeyboardInterrupt, EOFError):
            print("\n\n\033[91mUscita forzata rilevata. Ciaoooo!\033[0m")


main()

