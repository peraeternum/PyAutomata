from html.parser import incomplete

from automata.state import AutomatonState, By
from automata.transition import Transition


class Automaton:
    def __init__(self, name, description, allow_partial=False):
        self.type = None
        self.name = name
        self.description = description
        self.states = {}
        self.initial_state = None
        self.current_state = None
        self.current_states = None
        self.alphabet = set()
        self.stack_alphabet = set()
        self.allow_partial = allow_partial

    def add_state(self, name, is_final=False):
        state = AutomatonState(name, len(self.states), is_final)
        state.transitions = {}
        self.states[name] = state
        if not self.initial_state:
            self.initial_state = state
            self.current_state = state

    def _get_source_and_target(self, by, source, target):
        if by == By.NAME:
            source_state = self.states[source]
            target_state = self.states[target]
        elif by == By.ID:
            source_state = next(state for state in self.states.values() if state.id == source)
            target_state = next(state for state in self.states.values() if state.id == target)
        else:
            raise ValueError("Invalid value for 'by' parameter")

        return source_state, target_state

    def add_transition(self, source, symbol, target, by=By.NAME):
        if symbol not in self.alphabet:
            self.alphabet.add(symbol)

        source_state, target_state = self._get_source_and_target(by, source, target)

        transition = Transition(symbol, source_state, target_state)
        source_state.transitions[symbol] = transition

        if symbol in source_state.used_symbols:
            raise ValueError(f"Duplicate transition found for symbol '{symbol}'")
        source_state.used_symbols.add(symbol)

    def set_initial_state(self, identifier, by=By.NAME):
        if by == By.NAME:
            self.initial_state = self.states[identifier]
        elif by == By.ID:
            self.initial_state = next(state for state in self.states.values() if state.id == identifier)
        self.current_state = self.initial_state

    def check_automaton(self):
        incomplete_states = {}
        for state in self.states.values():
            missing = self.alphabet - state.used_symbols
            if missing:
                incomplete_states[state.name] = [symbol for symbol in missing]

        if incomplete_states:
            # Create a list of formatted strings for each state
            formatted_states = [
                f"State {state}: {', '.join(map(str, missing_symbols))}"
                for state, missing_symbols in incomplete_states.items()
            ]
            # Join the formatted strings with a newline character
            error_message = "\n".join(formatted_states)
            raise ValueError(f"Automaton is incomplete:\n{error_message}")

        return True

    def auto_complete(self):
        if self.type == "NFA":
            return

        uncomplete_states = {}
        for state in self.states.values():
            left = self.alphabet - state.used_symbols
            if left:
                uncomplete_states[state] = left






