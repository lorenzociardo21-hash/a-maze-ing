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
                    chiave = parti[0].strip()
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
            if self.exit[0] < 0 or self.exit[0] >= self.width or \
               self.exit[1] < 0 or self.exit[1] >= self.height:
                print("Errore: L'uscita è fuori dal labirinto!")
                sys.exit(1)
            if self.entry == self.exit:
                print("Errore: Entrata e uscita non possono essere nello stesso posto!")
        except KeyError as e:
            print(f"Errore: Manca la chiave obbligatoria {e}")
            sys.exit(1)
        except ValueError:
            print("Errore: Hai scritto una parola dove volevo un numero!")
        except Exception as e:
            print(f"Errore: {e}")
            sys.exit(1)
