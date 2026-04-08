DIRECTIONS = {
    "N": {"num": 1, "opposite": "S", "dx": 0, "dy": - 1},
    "S": {"num": 4, "opposite": "N", "dx": 0, "dy": 1},
    "E": {"num": 2, "opposite": "W", "dx": 1, "dy": 0},
    "W": {"num": 8, "opposite": "E", "dx": - 1, "dy": 0},
}

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
