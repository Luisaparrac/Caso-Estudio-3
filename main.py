from CuraduriaTramites import CuraduriaTramites


def process_file(file_name):
    system = CuraduriaTramites()

    try:
        file = open(file_name, "r", encoding="utf-8")
    except FileNotFoundError:
        print("Input file not found.")
        return

    with file:
        for line in file:
            line = line.strip()

            if line == "":
                continue

            if line.startswith("DEPENDENCIAS:"):
                continue

            if line.startswith("CAPACIDAD_BANDEJA:"):
                continue

            parts = line.split()

            if parts[0] == "RADICAR":
                day = int(parts[2].split("=")[1])
                applicant = parts[1]

                # This simple input format accepts names without spaces.
                system.radicacion = system.radicar(applicant, day)

            elif parts[0] == "FOLIO":
                radicado = parts[1]
                description = parts[2]
                system.add_folio(radicado, description)

            elif parts[0] == "ATENDER":
                system.attend_next(parts[1])

            elif parts[0] == "AVANZAR":
                system.advance(parts[1])

            elif parts[0] == "DEVOLVER":
                radicado = parts[1]
                observation = parts[2]
                system.return_expediente(radicado, observation)

            elif parts[0] == "ANULAR":
                radicado = parts[1]
                number = int(parts[2])
                system.cancel_folio(radicado, number)

            elif parts[0] == "IMPRIMIR":
                system.print_expediente(parts[1])

            elif parts[0] == "REPORTE":
                day = int(parts[1].split("=")[1])
                system.report(day)

            system.move_from_overflow()


if __name__ == "__main__":
    process_file("tramites.txt")
