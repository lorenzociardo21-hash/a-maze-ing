import os
import sys
from typing import Optional, Union, Dict

def find_file(filename: str, search_path: Optional[str] = os.getcwd()) -> str | None:
    for root, dirs, files in os.walk(search_path):
        if filename in files:
            return os.path.join(root, filename)
        return None



def configuration() -> Dict[str, str]:
    if len(sys.argv) == 1:
        with open("config.txt", 'w') as f:
            f.write("#Maze width (number of cells)\nWIDTH=20\n\
                    #Maze height\nHEIGHT=15\
                    \n#Entry coordinates (x, y)\nENTRY=0, 0\
                    \n#Exit coordinates (x, y)\nEXIT=19, 14\
                    \n#Output filename\nOUTPUT_FILE=maze.txt\
                    \n#Is the name perfect?\nPERFECT=True")
    with open(sys.argv[1], 'r') as f:
        maze_config = {k.strip().lower(): v.strip() for k, v in
                       (line.split("=")
                        for line in f.readlines()
                        if "=" in line
                        and not line.startswith("#"))}
    return maze_config

def validate_maze_val(maze_config: Dict[str, str]) -> None:
    if width := int(maze_config.get("width"), -1) <= 0 or width > os.terminal_size.columns:
        raise ValueError("The width of the maze cannot be 0 or less.")
    if height := int(maze_config.get("height"), -1) <= 0 or height > os.terminal_size.lines - 15:
        raise ValueError("The height of the maze cannot be 0 or less.")
    entry = maze_config.get("entry", (-1, -1))
    _exit = maze_config.get("exit", (-1, -1))
    if entry[0] < 0 or entry[0] >= width or entry[1] < 0 or entry[1] >= height:
        raise ValueError("The entry coordinates are wrong.")
    if _exit[0] < 0 or _exit[0] >= width or _exit[1] < 0 or _exit[1] >= height:
        raise ValueError("The exit coordinates are wrong.")
    #forse controllo all'outputfile, ad esempio se ha un formato valido
    perfect = maze_config.get("perfect", -1)
    if perfect not in (True, False):
        maze_config["perfect"] = True
