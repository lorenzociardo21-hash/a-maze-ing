from src.parser import mazeconfig


def output(griglia: list[list[int]],
           soluzione: list[tuple[int, int, str | None]],
           settings: mazeconfig) -> None:
    """Esporta il labirinto in formato esadecimale su file."""
    esadecimale: list[str] = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
                              "A", "B", "C", "D", "E", "F"]
    with open(settings.output_file, "w") as f:
        for riga in griglia:
            for valore in riga:
                f.write(esadecimale[valore])
            f.write("\n")
        f.write(f"\n{settings.entry[0]},{settings.entry[1]}\n")
        f.write(f"{settings.exit[0]},{settings.exit[1]}\n")
        for direzione in soluzione:
            if direzione[2] is not None:
                f.write(direzione[2])
        f.write("\n")
