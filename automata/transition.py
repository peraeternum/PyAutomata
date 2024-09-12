class Transition:
    def __init__(self, symbol, source, target, x=0, y=0):
        self.symbol = symbol
        self.source = source
        self.target = target
        self.x = x
        self.y = y

class MealyTransition(Transition):
    def __init__(self, symbol, source, target, output, x=0, y=0):
        super().__init__(symbol, source, target, x, y)
        self.output = output # Only used by Mealy machines