import time
from src.parser import mazeconfig

def change_config(file: str, change_settings: str,
                  settings: mazeconfig) -> int:
    try:
        key, value = change_settings.split("=", 1)
        value = value.strip()
        if key.upper() == "WIDTH" or key.upper() == "HEIGHT":
            width = int(value)
            if width <= 0:
                print("Errore: Larghezza e altezza devono \
essere numeri positivi!")
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
            values = value.split(",")
            entry = (int(values[0]), int(values[1]))
            if ((entry[0] < 0 or entry[0] > settings.width or
                 entry[1] < 0 or entry[1] > settings.height)):
                print("Errore: L'entrata è fuori dal labirinto!")
                time.sleep(1)
                return 0
            if entry == settings.exit or entry == settings.entry:
                print("Errore: Entrata e uscita non possono essere \
nello stesso posto!")
                time.sleep(1)
                return 0
            if entry in settings.pattern_cells:
                print("Errore: L'entrata o l'uscita cadono dentro il pattern 42!")
                time.sleep(1)
                return 0
        if key.upper() == "PERFECT":
            if value.capitalize() not in ["True", "False"]:
                print("Errore: ammessi solo True o False per l'impostazione Perfect!")
                time.sleep(1)
                return 0
        if key.upper() == "SEED":
            if value.capitalize() == "None":
                pass
            else:
                values = int(value)
                if values < 0:
                    print("Errore: il seed è negativo")
                    time.sleep(1)
                    return 0
    except KeyError as e:
        print(f"Errore: Manca la chiave obbligatoria {e}")
        time.sleep(1)
        return 0
    except ValueError:
        print("Errore: Hai scritto una parola dove volevo un numero!")
        time.sleep(1)
        return 0
    except Exception as e:
        print(f"Errore: {e}")
        time.sleep(1)
        return 0
    lines = []
    with open(file, 'r') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if not line.startswith("#") and "=" in line and line.find(key) != -1:
            line = line[:line.find("=") + 1] + value + "\n"
            lines[i] = line
    with open(file, 'w') as f:
        f.writelines(lines)
    return 1