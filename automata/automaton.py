from automata.state import By, State, AutomatonState, MooreState
from automata.transition import Transition, MealyTransition


class Automaton:
    def __init__(self, name, description, automaton_type, allow_partial=False):
        self.type = automaton_type
        self.name = name
        self.description = description
        self.states = {}
        self.initial_state = None
        self.current_state = None
        self.current_states = None
        self.alphabet = set()
        self.stack_alphabet = set('|')
        self.allow_partial = allow_partial
        self.inputs = []
        self.deterministic = True

        if self.type not in ["DPDA", "NPDA"]:
            self.add_transition = self._add_transition

    def process_input(self, simulation_input):
        print(f"Processing input '{simulation_input}' on automaton '{self.name}'")
        for symbol in simulation_input:
            if symbol not in self.alphabet:
                return False
            transition = self.current_state.transitions.get(symbol)
            if not transition:
                return False
            self.current_state = transition.target

        if self.type == 'DFA':
            return self.current_state.is_final
        elif self.type == "MOORE":
            return self.current_state.name, self.current_state.output if self.current_state.output is not None else None
        elif self.type == "MEALY":
            return self.current_state.name

    def add_state(self, name, state_id=None, is_final=False, output=None):
        if state_id is None:
            state_id = len(self.states) + 1
        if self.type == "MOORE":
            if output not in self.stack_alphabet:
                self.stack_alphabet.add(output)
            state = MooreState(name, state_id, output)
        elif self.type in ["DFA", "NFA", "NPDA", "DPDA"]:
            state = AutomatonState(name, state_id, is_final)
        else:
            state = State(name, state_id)
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

    def _add_transition(self, source, target, symbols, output=None, x=0, y=0, by=By.NAME):
        if isinstance(symbols, list):
            for symbol in symbols:
                if symbol not in self.alphabet:
                    self.alphabet.add(symbol)

            source_state, target_state = self._get_source_and_target(by, source, target)

            for symbol in symbols:
                if self.type == "MEALY":
                    if output not in self.stack_alphabet:
                        self.stack_alphabet.add(output)
                    transition = MealyTransition(
                        symbol=symbol,
                        source=source_state,
                        target=target_state,
                        output=output,
                        x=x, y=y
                    )
                else:
                    transition = Transition(
                        symbol=symbol,
                        source=source_state,
                        target=target_state,
                        x=x, y=y
                    )

                # For NFAs, store multiple transitions per symbol
                if self.type == "NFA":
                    if symbol not in source_state.transitions:
                        source_state.transitions[symbol] = []
                    source_state.transitions[symbol].append(transition)
                else:
                    # For DFAs and other types, keep the original behavior
                    if symbol in source_state.transitions:
                        raise ValueError(f"Duplicate transition found for symbol '{symbol}'")
                    source_state.transitions[symbol] = transition

                source_state.used_symbols.add(symbol)

        else:
            if symbols not in self.alphabet:    
                self.alphabet.add(symbols)

            source_state, target_state = self._get_source_and_target(by, source, target)

            if self.type == "MEALY":
                if output not in self.stack_alphabet:
                    self.stack_alphabet.add(output)
                transition = MealyTransition(symbols, source_state, target_state, output)
            else:
                transition = Transition(symbols, source_state, target_state)

            # For NFAs, store multiple transitions
            if self.type == "NFA":
                if symbols not in source_state.transitions:
                    source_state.transitions[symbols] = []
                source_state.transitions[symbols].append(transition)
            else:
                # For DFAs and other types, keep original behavior
                if symbols in source_state.transitions:
                    raise ValueError(f"Duplicate transition found for symbol '{symbols}'")
                source_state.transitions[symbols] = transition

            source_state.used_symbols.add(symbols)

    def add_input(self, simulation_input):
        self.inputs.append(simulation_input)

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
            formatted_states = [
                f"State {state}: {', '.join(map(str, missing_symbols))}"
                for state, missing_symbols in incomplete_states.items()
            ]
            error_message = "\n".join(formatted_states)
            raise ValueError(f"Automaton is incomplete:\n{error_message}")
        return True

    def auto_complete(self):
        if self.type == "NFA":
            return
        for state in self.states.values():
            missing = self.alphabet - state.used_symbols
            if missing:
                pass
        # Logic for completing transitions would go here