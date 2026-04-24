import time
import random
from src.parser import mazeconfig


def crea_pezzi_cella(valore_cella: int, x: int, y: int, settings: mazeconfig,
                     percorso_coords: list[tuple[int, int]],
                     risolvi: bool, colore: list[str]) -> tuple[str, str, str]:
    """ Genera le stringhe per il rendering della cella."""
    RESET = "\033[0m"
    MURO = colore[0] + "██" + RESET
    VUOTO = colore[1] + "██" + RESET
    ENTRY = "\033[92m" + "██" + RESET
    EXIT = "\033[91m" + "██" + RESET
    QUARANTADUE = colore[2] + "██" + RESET
    PATH_COLOR = "\033[92m" + "██" + RESET
    if valore_cella == 15:
        MURO = QUARANTADUE
        VUOTO = QUARANTADUE

    sopra = MURO
    mezzo = ""
    sotto = MURO

    if valore_cella & 1:  # il sopra
        sopra += MURO   # Chiudiamo il soffitto
    elif ((x, y - 1) in percorso_coords and risolvi
          and (x, y) in percorso_coords):
        sopra += PATH_COLOR
    else:
        sopra += VUOTO  # Lasciamo un buco
    sopra += MURO       # Chiudiamo l'angolo destro

    if valore_cella & 8:  # Muro a sinistra
        mezzo += MURO
    elif ((x - 1, y) in percorso_coords and risolvi
          and (x, y) in percorso_coords):
        mezzo += PATH_COLOR
    else:
        mezzo += VUOTO

    # Controllo per Entry, Exit e 42 e percorso
    if (x, y) == settings.entry:
        mezzo += ENTRY
    elif (x, y) == settings.exit:
        mezzo += EXIT
    elif valore_cella == 15:  # Cella chiusa per il pattern 42
        mezzo += QUARANTADUE
    elif (x, y) in percorso_coords and risolvi:
        mezzo += PATH_COLOR
    else:
        mezzo += VUOTO

    if valore_cella & 2:  # Muro a destra
        mezzo += MURO
    elif ((x + 1, y) in percorso_coords and risolvi
          and (x, y) in percorso_coords):
        mezzo += PATH_COLOR
    else:
        mezzo += VUOTO
    # il sotto(4)
    if valore_cella & 4:
        sotto += MURO
    elif ((x, y + 1) in percorso_coords and risolvi
          and (x, y) in percorso_coords):
        sotto += PATH_COLOR
    else:
        sotto += VUOTO
    sotto += MURO
    return sopra, mezzo, sotto


def sceltacolore(scelta_utente: int, colori_attuali: list[str]) -> list[str]:
    """ Gestisce la rotazione dei colori delle pareti."""
    palette = [
        "\033[95m", "\033[96m", "\033[97m", "\033[93m", "\033[94m", "\033[91m",
        "\033[92m", "\033[90m", "\033[31m", "\033[32m", "\033[33m", "\033[34m",
        "\033[35m", "\033[36m"
    ]

    if scelta_utente in [1, 2, 3]:
        idx_da_cambiare = scelta_utente - 1
        colore_vecchio = colori_attuali[idx_da_cambiare]
        try:
            indice_palette = palette.index(colore_vecchio)
        except ValueError:
            indice_palette = 0

        trovato = False
        while not trovato:
            indice_palette = (indice_palette + 1) % len(palette)
            nuovo_colore = palette[indice_palette]
            if nuovo_colore not in colori_attuali:
                trovato = True

        colori_attuali[idx_da_cambiare] = nuovo_colore
        return colori_attuali

    elif scelta_utente == 4:
        nuovicolori: list[str] = []
        for _ in colori_attuali:
            trovato = False
            while not trovato:
                indice_p = random.randint(0, len(palette) - 1)
                colore_pescato = palette[indice_p]
                if colore_pescato not in nuovicolori:
                    nuovicolori.append(colore_pescato)
                    trovato = True
        return nuovicolori
    return colori_attuali


def printamazing() -> None:
    """ Stampa il titolo ASCII dell'applicazione."""
    title = (
        "\n"
        "    █████           ███    ███   █████  ███████ ███████            "
        "██  ███    ██   ██████\n"
        "    ██   ██          ████  ████  ██   ██    ███  ██                "
        "██  ████   ██  ██\n"
        "    ███████   ███    ██ ████ ██  ███████   ███   █████     ███     "
        "██  ██ ██  ██  ██   ███\n"
        "    ██   ██          ██  ██  ██  ██   ██  ███    ██                "
        "██  ██  ██ ██  ██    ██\n"
        "    ██   ██          ██      ██  ██   ██ ███████ ███████           "
        "██  ██   ████   ██████\n"
    )
    print(title)


def disegna_maze(griglia: list[list[int]], settings: mazeconfig,
                 percorso: list[tuple[int, int, str | None]],
                 risolvi: bool, colore: list[str]) -> None:
    """ Gestisce il rendering completo del labirinto."""
    percorso_coords: list[tuple[int, int]] = []
    for cella in percorso:
        nuova_coppia = (cella[0], cella[1])
        percorso_coords.append(nuova_coppia)
    i: int = 0
    percorsofin: list[tuple[int, int]] = []
    if risolvi:
        while i < len(percorso):
            print("\033[2J\033[H\033[3J", end="")
            printamazing()
            percorsofin.append(percorso_coords[i])
            for y, riga_numeri in enumerate(griglia):
                linea_sopra = ""
                linea_mezzo = ""
                linea_sotto = ""
                for x, valore in enumerate(riga_numeri):
                    p_sopra, p_mezzo, p_sotto = crea_pezzi_cella(valore, x, y,
                                                                 settings,
                                                                 percorsofin,
                                                                 risolvi,
                                                                 colore)
                    linea_sopra += p_sopra
                    linea_mezzo += p_mezzo
                    linea_sotto += p_sotto
                print(linea_sopra)
                print(linea_mezzo)
                print(linea_sotto)
            i += 1
            time.sleep(0.1)

    else:
        print("\033[2J\033[H\033[3J", end="")
        printamazing()
        for y, riga_numeri in enumerate(griglia):
            linea_sopra = ""
            linea_mezzo = ""
            linea_sotto = ""
            for x, valore in enumerate(riga_numeri):
                p_sopra, p_mezzo, p_sotto = crea_pezzi_cella(valore, x,
                                                             y, settings,
                                                             percorso_coords,
                                                             risolvi, colore)
                linea_sopra += p_sopra
                linea_mezzo += p_mezzo
                linea_sotto += p_sotto
            print(linea_sopra)
            print(linea_mezzo)
            print(linea_sotto)
