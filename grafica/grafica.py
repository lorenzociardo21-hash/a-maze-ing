
def crea_pezzi_cella(valore_cella, x, y, settings):
    RESET = "\033[0m"
    MURO = "\033[95m" + "█" + RESET    
    VUOTO = "\033[96m" + "█" + RESET
    ENTRY = "\033[92m" + "E" + RESET
    EXIT = "\033[94m" + "X" + RESET
    QUARANTADUE = "\033[95m" + "█" + RESET 
    sopra = MURO
    mezzo = ""
    sotto = MURO
    if valore_cella & 1: # il sopra
        sopra += MURO   # Chiudiamo il soffitto
    else:
        sopra += VUOTO  # Lasciamo un buco
    sopra += MURO       # Chiudiamo l'angolo destro
    # destra e sinistra  8 e 2
    if valore_cella & 8: # Muro a sinistra
        mezzo += MURO
    else:
        mezzo += VUOTO
    
    # Controllo per Entry, Exit e 42
    if (x, y) == settings.entry:
        mezzo += ENTRY
    elif (x, y) == settings.exit:
        mezzo += EXIT
    elif valore_cella == 15: # Cella chiusa per il pattern 42 [cite: 140, 147]
        mezzo += QUARANTADUE
    else:
        mezzo += VUOTO 
        
    if valore_cella & 2: # Muro a destra
        mezzo += MURO
    else:
        mezzo += VUOTO
    # il sotto(4)
    if valore_cella & 4:
        sotto += MURO
    else:
        sotto += VUOTO
    sotto += MURO
    return sopra, mezzo, sotto

def disegna_maze(griglia, settings):
    for y, riga_numeri in enumerate(griglia):
        linea_sopra = ""
        linea_mezzo = ""
        linea_sotto = ""
        for x, valore in enumerate(riga_numeri):
            p_sopra, p_mezzo, p_sotto = crea_pezzi_cella(valore, x, y, settings)
            linea_sopra += p_sopra
            linea_mezzo += p_mezzo
            linea_sotto += p_sotto
        print(linea_sopra)
        print(linea_mezzo)
        print(linea_sotto)