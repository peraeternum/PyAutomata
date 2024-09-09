from automata.automaton import Automaton
from automata.state import By, AutomatonState
from automata.transition import Transition

class DFA(Automaton):
    def __init__(self, name=None, description=None):
        super().__init__(name, description)
        self.type = "DFA"

    def process_input(self, simulation_input):
        self.check_automaton()
        for symbol in simulation_input:
            if symbol not in self.alphabet:
                return False
            transition = self.current_state.transitions.get(symbol)
            if not transition:
                return False
            self.current_state = transition.target

        return self.current_state.is_final
