import sys
import time
from src.display import sceltacolore, printamazing, disegna_maze
from src.exporter import output
from src.parser import config, mazeconfig
from src.settings import change_config
from src.solver import  maze_res_mix_algo
from maze_gen.generator import MazeGenerator

def main() -> None:
    if len(sys.argv) != 2:
        print("Errore: Numero di argomenti sbagliato.")
        print("Usare: python3 a_maze_ing.py <config_file>")
        sys.exit(1)
    settings = mazeconfig(config(sys.argv[1]))
    maze = MazeGenerator(settings)
    indicealg = 0
    listaalg = [maze.generate_maze_kruskal, maze.generate_maze_prims,
                maze.generate_maze_dfs]
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
                if settings.seed != "None":
                    print("Non puoi generarlooo! hai impostato il seed!\
\nMetti il seed a None!!!")
                    time.sleep(4)
                griglia, seed = listaalg[indicealg]()
                soluzione = maze_res_mix_algo(maze, griglia)
                output(griglia, soluzione, settings)
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
                print("1. Kruskal | 2. Prims | 3. DFS")
                alg = input("Scegli un algoritmo!!! ")
                if alg in ["1", "2", "3"]:
                    indicealg = int(alg) - 1
            elif scelta == "5":
                input(f"Eccolooooo:\n{seed}\n\
\nPremi qualcoa e invio per continuare!")
            elif scelta == "6":
                print(f"\033[97m1. WIDTH:{settings.width}\033[0m")
                print(f"\033[97m2. HEIGHT:{settings.height}\033[0m")
                print(f"\033[97m3. ENTRY:{settings.entry}\033[0m")
                print(f"\033[97m4. EXIT:{settings.exit}\033[0m")
                print(f"\033[97m5. OUTPUT_FILE \
Name:{settings.output_file}\033[0m")
                print(f"\033[97m6. PERFECT:{settings.perfect}\033[0m")
                print(f"\033[97m7. SEED:{settings.seed}\033[0m")
                sceltaimp = input("\nscegli quello che vuoi cambiare!!")
                if sceltaimp in ["1", "2", "3", "4", "5", "6", "7"]:
                    impostazioni = ["WIDTH=", "HEIGHT=", "ENTRY=", "EXIT=",
                                    "OUTPUT_FILE=", "PERFECT=", "SEED="]
                    nv = input("Cambia il valore!")
                    nuovo_valore = impostazioni[int(sceltaimp) - 1] + nv
                    change_config(sys.argv[1], nuovo_valore, settings)
                    if not change_config:
                        print("hai sbagliato a scriverleee!!")
                        time.sleep(4)
                    else:
                        return main()

            elif scelta == "7":
                print("Ciaoooo")
                break
    except (KeyboardInterrupt, EOFError):
        print("\n\n\033[91mUscita forzata rilevata. Ciaoooo!\033[0m")


if __name__ == "__main__":
    main()