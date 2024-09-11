from automata.automaton import Automaton
from automata.state import By, AutomatonState
from automata.transition import Transition


def process_input(self, simulation_input):
    if not self.allow_partial:
        self.check_automaton()
    for symbol in simulation_input:
        if symbol not in self.alphabet:
            return False
        transition = self.current_state.transitions.get(symbol)
        if not transition:
            return False
        self.current_state = transition.target

    if self.type == 'DFA':
        return self.current_state.is_final
    else:
        return self.current_state.name, self.current_state.output if self.current_state.output is not None else None


class DFA(Automaton):
    def __init__(self, name='DFA', description=''):
        super().__init__(name, description)
        self.type = 'DFA'

    def process_input(self, simulation_input):
        return process_input(self, simulation_input)


class MOORE(Automaton):
    def __init__(self, name='MOORE', description=''):
        super().__init__(name, description)
        self.type = 'MOORE'

    def process_input(self, simulation_input):
        return process_input(self, simulation_input)

class MEALY(Automaton):
    def __init__(self, name='MEALY', description=''):
        super().__init__(name, description)
        self.type = 'MEALY'

    def process_input(self, simulation_input):
        return process_input(self, simulation_input)

