from QueueNode import QueueNode


class Queue:
    def __init__(self, capacity=20):
        self.front = None
        self.rear = None
        self.size = 0
        self.capacity = capacity

    def enqueue(self, value):
        if self.is_full():
            return False

        new_node = QueueNode(value)

        if self.front is None:
            self.front = new_node
        else:
            self.rear.next = new_node

        self.rear = new_node
        self.size += 1

        return True

    def dequeue(self):
        if self.front is None:
            return None

        value = self.front.value
        self.front = self.front.next

        if self.front is None:
            self.rear = None

        self.size -= 1

        return value

    def is_empty(self):
        return self.front is None

    def is_full(self):
        return self.size >= self.capacity

    def contains(self, value):
        current = self.front

        while current is not None:
            if current.value == value:
                return True
            current = current.next

        return False

    def print_queue(self):
        current = self.front
        text = ""

        while current is not None:
            if text != "":
                text += " | "

            text += current.value.radicado
            current = current.next

        return text
