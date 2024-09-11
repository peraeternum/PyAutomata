import random

class State:
    def __init__(self, name, state_id):
        self.name = name
        self.id = state_id
        self.transitions = {}
        self.used_symbols = set()
        self.x = random.randint(0, 1000)
        self.y = random.randint(0, 1000)
        self.radius = 30
        self.is_final = False

class AutomatonState(State):
    def __init__(self, name, state_id, is_final=False):
        super().__init__(name, state_id)
        self.is_final = is_final  # Only used by DFA and NFA
        self.epsilon_transitions = {}  # Only used by NFA


class MooreState(State):
    def __init__(self, name, state_id, output=None):
        super().__init__(name, state_id)
        self.output = output  # Only used by Moore machines



class By:
    NAME = 1
    ID = 2