from maze_gen.generator import MazeGenerator, DIRECTIONS

def get_neighbours(grid: list[list[int]], x: int, y: int,
                   visited: set) -> list[tuple[int, int, str]]:
    neighbours = []
    for direction, values in DIRECTIONS.items():
        if not grid[y][x] & values["num"]:
            nx, ny = x + values["dx"], y + values["dy"]
            if (nx, ny) not in visited:
                neighbours.append((nx, ny, direction))
    return neighbours


def distance(x1: int, y1: int, exit: tuple[int, int]) -> int:
    return ((exit[0] - x1) ** 2 + (exit[1] - y1) ** 2) ** 0.5


def find_dir(grid: list[list[int]], x: int, y: int, exit: tuple[int, int],
             visited: set) -> tuple[int, int, str]:
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


def check_stack(grid: list[list[int]],
                stack: list[tuple[int, int, str]]) -> None:
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


def check_distance(grid: list[list[int]],
                   neighbours: list[tuple[int, int, str]],
                   exit: tuple[int, int],
                   visited: set) -> tuple[int, int, str]:
    min_x, min_y, direction_min = neighbours[0]
    min_ndist, _, _, _ = find_dir(grid, min_x, min_y, exit,
                                  visited | {(min_x, min_y)})
    if (min_x, min_y) == exit:
        return min_x, min_y, direction_min
    for x, y, direction in neighbours[1:]:
        if ((distance(x, y, exit) < distance(min_x, min_y, exit)
             or (x, y) == exit)):
            next_dist, nx, ny, _ = find_dir(grid, x, y,
                                            exit, visited | {(x, y)})
            if next_dist < min_ndist or (nx, ny) == exit or (x, y) == exit:
                min_x, min_y, direction_min = x, y, direction
                min_ndist = next_dist
    return min_x, min_y, direction_min


def maze_res_astar(maze: MazeGenerator,
                   grid: list[list[int]]) -> list[tuple[int, int, str]]:
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


def maze_res_mix_algo(maze: MazeGenerator,
                      grid: list[list[int]]) -> list[tuple[int, int, str]]:
    visited = set()
    stack = []
    current_x, current_y = maze.entry
    visited.add((current_x, current_y))

    while (current_x, current_y) != maze.exit:
        neighbours = get_neighbours(grid, current_x, current_y, visited)

        if neighbours:
            nx, ny, direction = check_distance(grid,
                                               neighbours, maze.exit, visited)
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