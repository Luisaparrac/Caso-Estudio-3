class Folio:
    def __init__(self, number, description):
        self.number = number
        self.description = description
        self.status = "VIGENTE"

    def cancel(self):
        self.status = "ANULADO"

    def __str__(self):
        return f"folio {self.number} {self.description} {self.status}"
