from StackNode import StackNode


class RouteStack:
    def __init__(self):
        self.top = None
        self.size = 0

    def push(self, value):
        new_node = StackNode(value)
        new_node.next = self.top
        self.top = new_node
        self.size += 1

    def pop(self):
        if self.top is None:
            return None

        value = self.top.value
        self.top = self.top.next
        self.size -= 1

        return value

    def peek(self):
        if self.top is None:
            return None

        return self.top.value

    def is_empty(self):
        return self.top is None

    def copy(self):
        new_stack = RouteStack()
        temporary = RouteStack()

        current = self.top

        while current is not None:
            temporary.push(current.value)
            current = current.next

        while not temporary.is_empty():
            new_stack.push(temporary.pop())

        return new_stack

    def print_route(self):
        copy_stack = self.copy()
        route = ""

        while not copy_stack.is_empty():
            dependency = copy_stack.pop()

            if route != "":
                route += " > "

            route += dependency

        return route
