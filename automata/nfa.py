from automata.automaton import Automaton
from automata.state import By
from automata.transition import Transition


def epsilon_closure(state):
    closure = {state}
    # Use a stack or queue to explore all reachable states via ε-transitions
    stack = [state]

    while stack:
        current_state = stack.pop()
        for epsilon_state in current_state.epsilon_transitions:
            if epsilon_state not in closure:
                closure.add(epsilon_state)
                stack.append(epsilon_state)

    return closure


class NFA(Automaton):
    def __init__(self, name=None, description=None):
        super().__init__(name, description)
        self.type = "NFA"

    # Add epsilon transitions
    def add_epsilon_transition(self, source, target, by=By.NAME):
        source_state, target_state = self._get_source_and_target(by, source, target)

        transition = Transition([""], source_state, target_state)
        source_state.epsilon_transitions[target_state] = transition

    def process_input(self, simulation_input):
        # Start with the epsilon-closure of the initial state
        self.current_states = epsilon_closure(self.initial_state)

        for symbol in simulation_input:
            if symbol not in self.alphabet:
                return False

            next_states = set()
            for state in self.current_states:
                for transition in state.transitions.values():
                    if symbol in transition.symbol:
                        next_states.add(transition.target)

            self.current_states = set()
            for state in next_states:
                self.current_states.update(epsilon_closure(state))


        # Check if any of the current states are accepting
        accepting_states = [state for state in self.current_states if state.is_final]
        return bool(accepting_states)