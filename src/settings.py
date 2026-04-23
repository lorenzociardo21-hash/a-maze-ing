import time
from src.parser import mazeconfig


def change_config(file: str, change_settings: str,
                  settings: mazeconfig) -> int:
    """Modifica i parametri nel file di configurazione."""
    key: str = ""
    value: str = ""

    try:
        key, value = change_settings.split("=", 1)
        value = value.strip()

        if key.upper() == "WIDTH" or key.upper() == "HEIGHT":
            width: int = int(value)
            if width <= 0:
                print("Errore: Larghezza e altezza devono essere positivi!")
                time.sleep(1)
                return 0
            if key.upper() == "WIDTH":
                if width < settings.entry[0] or width < settings.exit[0]:
                    print("Errore: DIOCANEEEEEEEEE")
                    time.sleep(1)
                    return 1
            if key.upper() == "HEIGHT":
                if width < settings.entry[1] or width < settings.exit[1]:
                    print("Errore: L'altezza non può essere più piccola dell'entrata o dell'uscita")
                    time.sleep(1)
                    return 1

        if key.upper() == "ENTRY" or key.upper() == "EXIT":
            parts: list[str] = value.split(",")
            entry_coord: tuple[int, int] = (int(parts[0]), int(parts[1]))
            if ((entry_coord[0] < 0 or entry_coord[0] > settings.width or
                 entry_coord[1] < 0 or entry_coord[1] > settings.height)):
                print("Errore: L'entrata è fuori dal labirinto!")
                time.sleep(1)
                return 0
            if entry_coord == settings.exit or entry_coord == settings.entry:
                print("Errore: Entrata e uscita non possono coincidere!")
                time.sleep(1)
                return 0
<<<<<<< HEAD
            if entry in settings.pattern_cells:
                print("Errore: L'entrata o l'uscita cadono dentro il pattern 42!")
                time.sleep(1)
                return 0
=======

>>>>>>> 4b9b29d7546e90d0fe48454a0af18eea9f62598d
        if key.upper() == "PERFECT":
            if value.capitalize() not in ["True", "False"]:
                print("Errore: ammessi solo True o False per l'impostazione Perfect!")
                time.sleep(1)
                return 0

        if key.upper() == "SEED":
            if value.capitalize() == "None":
                pass
            else:
<<<<<<< HEAD
                values = int(value)
                if values < 0:
                    print("Errore: il seed è negativo")
                    time.sleep(1)
=======
                seed_val: int = int(value)
                if seed_val < 0:
>>>>>>> 4b9b29d7546e90d0fe48454a0af18eea9f62598d
                    return 0

    except (KeyError, ValueError, Exception):
        time.sleep(1)
        return 0

    lines: list[str] = []
    with open(file, 'r') as f:
        lines = f.readlines()

    i: int
    line: str
    for i, line in enumerate(lines):
        if not line.startswith("#") and "=" in line and line.find(key) != -1:
            line = line[:line.find("=") + 1] + value + "\n"
            lines[i] = line

    with open(file, 'w') as f:
        f.writelines(lines)
    return 1
