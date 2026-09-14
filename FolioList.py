from FolioNode import FolioNode
from Folio import Folio


class FolioList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def add(self, description):
        folio = Folio(self.size + 1, description)
        new_node = FolioNode(folio)

        if self.head is None:
            self.head = new_node
        else:
            self.tail.next = new_node

        self.tail = new_node
        self.size += 1

        return folio

    def find(self, number):
        current = self.head

        while current is not None:
            if current.folio.number == number:
                return current.folio
            current = current.next

        return None

    def count_valid(self):
        count = 0
        current = self.head

        while current is not None:
            if current.folio.status == "VIGENTE":
                count += 1
            current = current.next

        return count

    def count_cancelled(self):
        count = 0
        current = self.head

        while current is not None:
            if current.folio.status == "ANULADO":
                count += 1
            current = current.next

        return count

    def print_all(self):
        current = self.head

        while current is not None:
            print(
                f"folio {current.folio.number} "
                f"{current.folio.description} "
                f"{current.folio.status}"
            )
            current = current.next
