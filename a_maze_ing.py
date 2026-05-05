import sys
import time
from collections.abc import Callable
from src.display import sceltacolore, printamazing, disegna_maze
from src.exporter import output
from src.parser import config, mazeconfig
from src.settings import change_config
from src.solver import maze_res_mix_algo, maze_res_astar
from maze_gen.generator import MazeGenerator


def main() -> None:
    '''fa quello che fanno i main'''
    if len(sys.argv) != 2:
        print("Errore: Numero di argomenti sbagliato.")
        print("Usare: python3 a_maze_ing.py <config_file>")
        sys.exit(1)
    ngs: mazeconfig = mazeconfig(config(sys.argv[1]))
    maze: MazeGenerator = MazeGenerator(ngs.width,
                                        ngs.height, ngs.entry,
                                        ngs.exit, ngs.perfect,
                                        ngs.seed, ngs.pattern_cells)
    indicealg: int = 0
    listaalg: list[Callable[[], tuple[list[list[int]], int]]] = [
        maze.generate_maze_kruskal,
        maze.generate_maze_prims,
        maze.generate_maze_dfs,
    ]
    griglia: list[list[int]]
    seed: int
    griglia, seed = listaalg[indicealg]()
    soluzione = maze_res_mix_algo(maze, griglia)
    output(griglia, soluzione, ngs)
    colore: list[str] = ["\033[95m", "\033[97m", "\033[93m"]
    risolvi: bool = False
    printamazing()
    algsoluzione: bool = False
    try:
        while True:
            print("\033[2J\033[H\033[3J", end="")
            disegna_maze(griglia, ngs, soluzione, risolvi, colore)
            print("\n\033[91m1. Generare nuovo labirinto\033[0m")
            print("\033[95m2. Mostrate percorso\033[0m")
            print("\033[97m3. Cambiare colore\033[0m")
            print("\033[97m4. Cambia algoritmo\033[0m")
            print("\033[97m5. Vuoi il seed????\033[0m")
            print("\033[97m6. Scegli le TUE impostazioni!\033[0m")
            if not algsoluzione:
                print("\033[97m7. Cambia algoritmo risoluzione! \
ora stai usando: Coglione\033[0m")
            else:
                print("\033[97m7. Cambia algoritmo risoluzione! \
ora stai usando: Astar\033[0m")
            print("\033[93m8. Uscire\033[0m")
            scelta = input("\nscegliiiiii: ")
            if scelta == "1":
                risolvi = False
                if ngs.seed != "None":
                    print("Non puoi generarlooo! hai impostato il seed!\
\nMetti il seed a None!!!")
                    time.sleep(4)
                griglia, seed = listaalg[indicealg]()
                if not algsoluzione:
                    soluzione = maze_res_mix_algo(maze, griglia)
                else:
                    soluzione = maze_res_astar(maze, griglia)
                output(griglia, soluzione, ngs)
            elif scelta == "2":
                risolvi = not risolvi
            elif scelta == "3":
                risolvi = False
                print("1. Muri | 2. Corridoio | 3. 42 | \
4. Scelta pazzerella")
                quale = input("Quale parte vuoi cambiare? ")
                if quale in ["1", "2", "3", "4"]:
                    colore = sceltacolore(int(quale), colore)
            elif scelta == "4":
                risolvi = False
                print("1. Kruskal | 2. Prims | 3. DFS")
                alg = input("Scegli un algoritmo!!! ")
                if alg in ["1", "2", "3"]:
                    indicealg = int(alg) - 1
            elif scelta == "5":
                risolvi = False
                input(f"Eccolooooo:\n{seed}\n\
\nPremi qualcoa e invio per continuare!")
            elif scelta == "6":
                risolvi = False
                print(f"\033[97m1. WIDTH: {ngs.width}\033[0m")
                print(f"\033[97m2. HEIGHT: {ngs.height}\033[0m")
                print(f"\033[97m3. ENTRY: {ngs.entry}\033[0m")
                print(f"\033[97m4. EXIT: {ngs.exit}\033[0m")
                print(f"\033[97m5. OUTPUT_FILE \
Name: {ngs.output_file}\033[0m")
                print(f"\033[97m6. PERFECT: {ngs.perfect}\033[0m")
                print(f"\033[97m7. SEED: {ngs.seed}\033[0m")
                sceltaimp = input("\nscegli quello che vuoi cambiare!!")
                if sceltaimp in ["1", "2", "3", "4", "5", "6", "7"]:
                    impostazioni: list[str] = [
                        "WIDTH=", "HEIGHT=", "ENTRY=", "EXIT=",
                        "OUTPUT_FILE=", "PERFECT=", "SEED=",
                    ]
                    nv = input("Cambia il valore!")
                    nuovo_valore = impostazioni[int(sceltaimp) - 1] + nv
                    result = change_config(sys.argv[1], nuovo_valore, ngs)
                    if not result:
                        print("hai sbagliato a scriverleee!!")
                        time.sleep(4)
                    else:
                        return main()
            elif scelta == "7":
                risolvi = False
                print("1. Coglione algoritm | 2. Astar algoritm")
                sceltariso: str = input("scegliii")
                if sceltariso == "1":
                    algsoluzione = False
                    soluzione = maze_res_mix_algo(maze, griglia)
                elif sceltariso == "2":
                    algsoluzione = True
                    soluzione = maze_res_astar(maze, griglia)

            elif scelta == "8":
                risolvi = False
                print("Ciaoooo")
                break
    except (KeyboardInterrupt, EOFError):
        print("\n\n\033[91mUscita forzata rilevata. Ciaoooo!\033[0m")


if __name__ == "__main__":
    main()
