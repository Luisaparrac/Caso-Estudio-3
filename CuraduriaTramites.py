from Queue import Queue
from Expediente import Expediente


class CuraduriaTramites:
    def __init__(self):
        self.reception = Queue(20)
        self.legal = Queue(20)
        self.technical = Queue(20)
        self.urban = Queue(20)
        self.resolution = Queue(20)

        self.general_overflow = Queue(1000)

        self.archived_count = 0
        self.resolved_count = 0
        self.next_number = 1

        self.total_returns_reception = 0
        self.total_returns_legal = 0
        self.total_returns_technical = 0
        self.total_returns_urban = 0

    def generate_radicado(self):
        radicado = f"11001-2026-{self.next_number:04d}"
        self.next_number += 1
        return radicado

    def get_queue(self, dependency):
        if dependency == "RECEPCION":
            return self.reception
        if dependency == "JURIDICA":
            return self.legal
        if dependency == "TECNICA":
            return self.technical
        if dependency == "URBANISTICA":
            return self.urban
        if dependency == "RESOLUCION":
            return self.resolution

        return None

    def find_expediente_in_queue(self, radicado):
        queues = (
            self.reception,
            self.legal,
            self.technical,
            self.urban,
            self.resolution
        )

        index = 0
        while index < 5:
            current = queues[index].front

            while current is not None:
                if current.value.radicado == radicado:
                    return current.value
                current = current.next

            index += 1

        return None

    def radicar(self, applicant, day):
        radicado = self.generate_radicado()
        expediente = Expediente(radicado, applicant, day)

        if not self.reception.enqueue(expediente):
            self.general_overflow.enqueue(expediente)

        print(f"RADICADO: {radicado}")
        return expediente

    def add_folio(self, radicado, description):
        expediente = self.find_expediente_in_queue(radicado)

        if expediente is None:
            print("Expediente not found.")
            return False

        folio = expediente.add_folio(description)
        print(f"Folio {folio.number} added.")
        return True

    def cancel_folio(self, radicado, number):
        expediente = self.find_expediente_in_queue(radicado)

        if expediente is None:
            print("Expediente not found.")
            return False

        success, message = expediente.cancel_folio(number)
        print(message)
        return success

    def attend_next(self, dependency):
        queue = self.get_queue(dependency)

        if queue is None:
            print("Invalid dependency.")
            return None

        expediente = queue.dequeue()

        if expediente is None:
            print(f"No expedientes in {dependency}.")
            return None

        expediente.ready_for_decision = True

        print(
            f"ATTENDING {expediente.radicado} "
            f"in {dependency}"
        )

        return expediente

    def move_from_overflow(self):
        if self.general_overflow.is_empty():
            return

        current = self.general_overflow.front

        while current is not None:
            expediente = current.value
            destination = self.get_queue(expediente.current_dependency)

            if not destination.is_full():
                self.general_overflow.dequeue()
                destination.enqueue(expediente)
                return

            current = current.next

    def advance(self, radicado):
        expediente = self.find_expediente_in_queue(radicado)

        if expediente is None:
            print("Expediente not found in a queue.")
            return False

        if not expediente.ready_for_decision:
            print("The expediente must be attended before advancing.")
            return False

        current = expediente.current_dependency

        if current == "RECEPCION":
            next_dependency = "JURIDICA"
        elif current == "JURIDICA":
            next_dependency = "TECNICA"
        elif current == "TECNICA":
            next_dependency = "URBANISTICA"
        elif current == "URBANISTICA":
            next_dependency = "RESOLUCION"
        else:
            print("The expediente is already in RESOLUCION.")
            return False

        if next_dependency == "RESOLUCION" and expediente.get_valid_folios() < 4:
            print("Cannot advance: at least 4 valid folios are required.")
            return False

        destination = self.get_queue(next_dependency)

        if destination.is_full():
            print("Destination queue is full. Expediente goes to overflow.")
            self.general_overflow.enqueue(expediente)
            return False

        # Remove it from its current queue.
        self.remove_from_queue(self.get_queue(current), expediente)

        expediente.current_dependency = next_dependency
        expediente.route.push(next_dependency)
        expediente.ready_for_decision = False
        destination.enqueue(expediente)

        if next_dependency == "RESOLUCION":
            # It is only ready for resolution after being attended there.
            pass

        print(
            f"{expediente.radicado}: "
            f"{current} -> {next_dependency}"
        )

        return True

    def remove_from_queue(self, queue, target):
        previous = None
        current = queue.front

        while current is not None:
            if current.value == target:
                if previous is None:
                    queue.front = current.next
                else:
                    previous.next = current.next

                if current == queue.rear:
                    queue.rear = previous

                queue.size -= 1
                return True

            previous = current
            current = current.next

        return False

    def return_expediente(self, radicado, observation):
        expediente = self.find_expediente_in_queue(radicado)

        if expediente is None:
            print("Expediente not found.")
            return False

        current = expediente.current_dependency

        if current == "RECEPCION":
            print("An expediente in RECEPCION cannot be returned.")
            return False

        old_dependency = expediente.route.pop()

        if old_dependency != current:
            print("Route error.")
            return False

        previous_dependency = expediente.route.peek()

        if previous_dependency is None:
            print("There is no previous dependency.")
            return False

        previous_queue = self.get_queue(previous_dependency)

        self.remove_from_queue(self.get_queue(current), expediente)

        if previous_queue.is_full():
            self.general_overflow.enqueue(expediente)
        else:
            previous_queue.enqueue(expediente)

        expediente.current_dependency = previous_dependency
        expediente.ready_for_decision = False
        expediente.returns += 1

        if current == "RECEPCION":
            self.total_returns_reception += 1
        elif current == "JURIDICA":
            self.total_returns_legal += 1
        elif current == "TECNICA":
            self.total_returns_technical += 1
        elif current == "URBANISTICA":
            self.total_returns_urban += 1

        print(f"Observation: {observation}")
        print(
            f"Route before return: "
            f"{expediente.route.print_route()} > {current}"
        )
        print(
            f"{current} removed from route -> "
            f"returns to {previous_dependency}"
        )
        print(
            f"returns = {expediente.returns} of 3"
        )

        if expediente.returns >= 3:
            self.remove_from_queue(previous_queue, expediente)
            expediente.archived = True
            self.archived_count += 1
            print("Expediente archived by withdrawal.")

        return True

    def resolve(self, radicado):
        expediente = self.find_expediente_in_queue(radicado)

        if expediente is None:
            print("Expediente not found.")
            return False

        if expediente.current_dependency != "RESOLUCION":
            print("Expediente is not in RESOLUCION.")
            return False

        if not expediente.ready_for_decision:
            print("The resolution queue must attend the expediente first.")
            return False

        self.remove_from_queue(self.resolution, expediente)
        expediente.resolved = True
        self.resolved_count += 1
        print(f"Expediente {radicado} resolved.")
        return True

    def print_expediente(self, radicado):
        expediente = self.find_expediente_in_queue(radicado)

        if expediente is None:
            print("Expediente not found.")
            return False

        print(
            f"EXPEDIENTE {expediente.radicado} | "
            f"{expediente.applicant} | "
            f"current dependency: {expediente.current_dependency}"
        )

        expediente.folios.print_all()

        print(
            f"folios: {expediente.get_total_folios()} total, "
            f"{expediente.get_valid_folios()} valid, "
            f"{expediente.get_cancelled_folios()} cancelled"
        )

        print(
            f"route: {expediente.route.print_route()} "
            f"(stack intact)"
        )

        return True

    def report(self, current_day):
        self.update_expired(current_day)

        print(f"\n=== REPORT DAY {current_day} ===")
        print(
            f"Queues: RECEPCION {self.reception.size} | "
            f"JURIDICA {self.legal.size} | "
            f"TECNICA {self.technical.size} | "
            f"URBANISTICA {self.urban.size} | "
            f"RESOLUCION {self.resolution.size}"
        )

        print(
            f"Overflow: {self.general_overflow.size} | "
            f"Archived by R3: {self.archived_count} | "
            f"Resolved: {self.resolved_count}"
        )

        print(
            "Returns by dependency: "
            f"RECEPCION {self.total_returns_reception} | "
            f"JURIDICA {self.total_returns_legal} | "
            f"TECNICA {self.total_returns_technical} | "
            f"URBANISTICA {self.total_returns_urban}"
        )

        self.print_expired(current_day)

    def update_expired(self, current_day):
        queues = (
            self.reception,
            self.legal,
            self.technical,
            self.urban,
            self.resolution,
            self.general_overflow
        )

        index = 0
        while index < 6:
            current = queues[index].front

            while current is not None:
                current.value.mark_expired(current_day)
                current = current.next

            index += 1

    def print_expired(self, current_day):
        print("EXPIRED (R6):")

        queues = (
            self.reception,
            self.legal,
            self.technical,
            self.urban,
            self.resolution,
            self.general_overflow
        )

        found = False
        index = 0

        while index < 6:
            current = queues[index].front

            while current is not None:
                expediente = current.value

                if current_day - expediente.registration_day > 45:
                    days = current_day - expediente.registration_day
                    print(
                        f"{expediente.radicado} "
                        f"({days} working days)"
                    )
                    found = True

                current = current.next

            index += 1

        if not found:
            print("None")

    def print_dependency_status(self):
        print("\nCURRENT DEPENDENCY STATUS")
        print(f"RECEPCION: {self.reception.size}")
        print(f"JURIDICA: {self.legal.size}")
        print(f"TECNICA: {self.technical.size}")
        print(f"URBANISTICA: {self.urban.size}")
        print(f"RESOLUCION: {self.resolution.size}")
        print(f"OVERFLOW: {self.general_overflow.size}")
