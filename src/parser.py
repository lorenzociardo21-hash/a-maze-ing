import sys
import time


PATTERN_42 = [
    (0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 3), (2, 4),  # 4
    (4, 0), (5, 0), (6, 0), (6, 1), (6, 2), (5, 2), (4, 2), (4, 3),
    (4, 4), (5, 4), (6, 4),  # 2
]


def pattern42(width: int, height: int) -> set[tuple[int, int]]:
    '''calcola dove mettere il 42'''
    center_x = width // 2 - 3
    center_y = height // 2 - 2
    return {(center_x + dx, center_y + dy) for dx, dy in PATTERN_42}


def can_show_pattern(width: int, height: int) -> bool:
    '''controlla se c'e' posto per il 42'''
    return width >= 10 and height >= 7


def config(namefile: str) -> dict[str, str]:
    '''legge il file!'''
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
    ''' genere una classe con tutte le impostazini(tooop)'''
    def __init__(self, dati_estratti: dict[str, str]) -> None:
        self.width: int = -1
        self.height: int = -1
        self.entry: tuple[int, int] = (-1, -1)
        self.exit: tuple[int, int] = (-1, -1)
        self.output_file: str = ""
        self.perfect: bool = False
        self.seed: str | None = None
        self.pattern_cells: set[tuple[int, int]] = set()

        try:
            self.width = int(dati_estratti["WIDTH"])
            self.height = int(dati_estratti["HEIGHT"])
            e_parti = dati_estratti["ENTRY"].split(",")
            self.entry = (int(e_parti[0]), int(e_parti[1]))
            x_parti = dati_estratti["EXIT"].split(",")
            self.exit = (int(x_parti[0]), int(x_parti[1]))
            self.output_file = dati_estratti["OUTPUT_FILE"]
            self.perfect = dati_estratti["PERFECT"] == "True"
            self.seed = dati_estratti["SEED"].capitalize()
            if self.entry[0] < 0 or self.entry[0] >= self.width or \
               self.entry[1] < 0 or self.entry[1] >= self.height:
                print("Errore: L'entrata è fuori dal labirinto!")
                sys.exit(1)
            if self.exit[0] < 0 or self.exit[0] >= self.width or \
               self.exit[1] < 0 or self.exit[1] >= self.height:
                print("Errore: L'uscita è fuori dal labirinto!")
                sys.exit(1)
            if self.entry == self.exit:
                print("Errore: Entrata e uscita non possono essere \
nello stesso posto!")
            if self.width <= 0 or self.height <= 0:
                print("Errore: Larghezza e altezza devono essere \
numeri positivi!")
                sys.exit(1)
            if can_show_pattern(self.width, self.height):
                self.pattern_cells = pattern42(self.width, self.height)
            else:
                print("\033[2J\033[H\033[3J", end="")
                print("Il 42 non c'entra, coglione")
                time.sleep(2.5)
            if ((self.entry in self.pattern_cells
                 or self.exit in self.pattern_cells)):
                print("Errore: L'entrata o l'uscita cadono \
dentro il pattern 42!")
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
