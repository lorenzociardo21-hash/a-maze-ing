import random


class MazeGenerator:
    def __init__(self, maze) -> None:
        self.maze_width: int = maze.width
        self.maze_height: int = maze.height
        self.maze_entry: tuple = maze.entry
        self.maze_exit: tuple = maze.exit
        self.perfect: bool = maze.perfect
        self.visited_cells = []

    def create_grid(self):
        return [[15 for _ in range(self.maze_width)] for _ in range(self.maze_height)]

    def generate_maze(self):
        frontiera = []
        grid = self.create_grid()
        self.visited_cells.extend([(self.maze_entry[0], self.maze_entry[1]), (self.maze_exit[0], self.maze_exit[1])])
        
