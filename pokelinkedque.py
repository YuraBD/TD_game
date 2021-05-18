from linkedque import LinkedQueue

class PokeQueue(LinkedQueue):
    def __init__(self):
        self._pokes = LinkedQueue()

    def add_poke(self, poke):
        self._pokes.add(poke)

    def remove_poke(self):
        return self._pokes.pop()

    def get_first_poke(self):
        return self._pokes.peek()

    def draw(self):
        for poke in self._pokes:
            poke.draw()
            poke.draw_hp()

    def draw_hit_boxes(self, color = (0, 0, 0, 255), line_thickness: float = 1):
        """ Draw all the hit boxes in this list """
        for poke in self._pokes:
            poke.draw_hit_box(color, line_thickness)

    def insert_poke(self, poke):
        pos = 0
        for line_poke in self._pokes:
            if poke.center_x > line_poke.center_x:
                break
            pos += 1
        self._pokes.insert(poke, pos)