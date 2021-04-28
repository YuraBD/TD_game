from linkedque import LinkedQueue

class PokeQueue(LinkedQueue):
    def __init__(self):
        self._pokes = LinkedQueue()

    def add_poke(self, poke):
        self._pokes.add(poke)

    def remove_poke(self):
        self._pokes.pop()

    def get_first_poke(self):
        return self._pokes.peek()

    def draw(self):
        for poke in self._pokes:
            poke.draw()