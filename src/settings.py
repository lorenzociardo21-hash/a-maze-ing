import time
from src.parser import mazeconfig, can_show_pattern, pattern42


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
                if can_show_pattern(width, settings.height):
                    pattern43: set[tuple[int,
                                         int]] = pattern42(width,
                                                           settings.height)
                    if ((settings.entry in pattern43 or
                         settings.exit in pattern43)):
                        print("Errore: Sei dentro il 42")
                        time.sleep(1)
                        return 0
                if width <= settings.entry[0] or width <= settings.exit[0]:
                    print("Errore: Coglione")
                    time.sleep(1)
                    return 0
            if key.upper() == "HEIGHT":
                if can_show_pattern(settings.width, width):
                    pattern43 = pattern42(settings.width, width)
                    if ((settings.entry in pattern43 or
                         settings.exit in pattern43)):
                        print("Errore: Sei dentro il 42")
                        time.sleep(1)
                        return 0
                if width <= settings.entry[1] or width <= settings.exit[1]:
                    print("Errore: L'altezza non può essere più \
piccola dell'entrata o dell'uscita")
                    time.sleep(1)
                    return 0

        if key.upper() == "ENTRY" or key.upper() == "EXIT":
            parts: list[str] = value.split(",")
            entry_coord: tuple[int, int] = (int(parts[0]), int(parts[1]))
            if ((entry_coord[0] < 0 or entry_coord[0] >= settings.width or
                 entry_coord[1] < 0 or entry_coord[1] >= settings.height)):
                print("Errore: L'entrata è fuori dal labirinto!")
                time.sleep(1)
                return 0
            if entry_coord == settings.exit or entry_coord == settings.entry:
                print("Errore: Entrata e uscita non possono coincidere!")
                time.sleep(1)
                return 0
            if entry_coord in settings.pattern_cells:
                print("Errore: L'entrata o l'uscita cadono dentro \
il pattern 42!")
                time.sleep(1)
                return 0
        if key.upper() == "PERFECT":
            value = value.capitalize()
            if value not in ["True", "False"]:
                print("Errore: ammessi solo True o False per \
l'impostazione Perfect!")
                time.sleep(1)
                return 0

        if key.upper() == "SEED":
            if value.capitalize() == "None":
                pass
            else:
                values_int: int = int(value)
                if values_int < 0:
                    print("Errore: il seed è negativo")
                    time.sleep(1)
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
