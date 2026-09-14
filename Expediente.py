from FolioList import FolioList
from RouteStack import RouteStack


class Expediente:
    def __init__(self, radicado, applicant, registration_day):
        self.radicado = radicado
        self.applicant = applicant
        self.current_dependency = "RECEPCION"
        self.returns = 0
        self.registration_day = registration_day
        self.folios = FolioList()
        self.route = RouteStack()
        self.ready_for_decision = False
        self.archived = False
        self.resolved = False
        self.expired = False

        # The first folio is always the application.
        self.folios.add("solicitud")
        self.route.push("RECEPCION")

    def add_folio(self, description):
        return self.folios.add(description)

    def cancel_folio(self, number):
        folio = self.folios.find(number)

        if folio is None:
            return False, "Folio does not exist."

        if folio.status == "ANULADO":
            return False, "Folio is already cancelled."

        folio.cancel()
        return True, "Folio cancelled."

    def mark_expired(self, current_day):
        if current_day - self.registration_day > 45:
            self.expired = True

    def get_total_folios(self):
        return self.folios.size

    def get_valid_folios(self):
        return self.folios.count_valid()

    def get_cancelled_folios(self):
        return self.folios.count_cancelled()
