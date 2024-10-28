from typing import List, Set, Tuple, Union

from automata.automaton import Automaton
from automata.state import By, State
from automata.transition import PDATransition, Transition


class DFA(Automaton):
    def __init__(self, name='DFA', description='', allow_partial=False):
        super().__init__(name, description, 'DFA', allow_partial)

class MOORE(Automaton):
    def __init__(self, name='MOORE', description='', allow_partial=False):
        super().__init__(name, description, 'MOORE', allow_partial)

class MEALY(Automaton):
    def __init__(self, name='MEALY', description='', allow_partial=False):
        super().__init__(name, description,  'MEALY', allow_partial)


class NFA(Automaton):
    def __init__(self, name=None, description=None):
        super().__init__(name, description, 'NFA')

    # Add epsilon transitions for non-deterministic automata
    def add_epsilon_transition(self, source, target, by=By.NAME):
        source_state, target_state = self._get_source_and_target(by, source, target)

        transition = Transition([""], source_state, target_state)
        source_state.epsilon_transitions[target_state] = transition


    @staticmethod
    def _epsilon_closure(state):
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


    def process_input(self, simulation_input):
        # Check if the NFA has any epsilon transitions
        has_epsilon_transitions = any(
            any(transition.symbol == '' for transitions in state.transitions.values()
                for transition in (transitions if isinstance(transitions, list) else [transitions]))
            for state in self.states.values()
        )

        # Start with initial state and its epsilon closure if needed
        self.current_states = {self.initial_state}
        if has_epsilon_transitions:
            self.current_states = self._epsilon_closure(self.initial_state)

        for symbol in simulation_input:
            if symbol not in self.alphabet:
                return False

            # Get all possible next states from all current states
            next_states = set()
            for current_state in self.current_states:

                # Get all transitions for the current state and symbol
                if symbol in current_state.transitions:
                    transitions = current_state.transitions[symbol]
                    if not isinstance(transitions, list):
                        transitions = [transitions]  # Handle both old and new format

                    for transition in transitions:
                        next_states.add(transition.target)

            # If no valid transitions were found, the input is rejected
            if not next_states:
                return False

            # Update current states, including epsilon closures if needed
            self.current_states = next_states
            if has_epsilon_transitions:
                epsilon_closure_states = set()
                for state in next_states:
                    closure_states = self._epsilon_closure(state)
                    epsilon_closure_states.update(closure_states)
                self.current_states = epsilon_closure_states


        # After processing input, check for acceptance
        accepting_states = [state for state in self.current_states if state.is_final]

        return bool(accepting_states)


class DPDA(Automaton):
    def __init__(self, name='DPDA', description='', require_empty_stack=False):
        super().__init__(name, description, 'DPDA')
        self.initial_stack: List[str] = ['|']  # Initialize with bottom marker
        self.stack: List[str] = self.initial_stack
        self.stack_alphabet: Set[str] = set('|')  # Initialize with bottom marker
        self.require_empty_stack = require_empty_stack

    def add_transition(self, source: str, target: str, symbol: Union[str, List[str]],
                       stack_symbol: str, stack_push: List[str], by=By.NAME) -> None:
        """
        Add a transition for DPDA

        Args:
            source: Source state name/id
            target: Target state name/id
            symbol: Input symbol (str for a single symbol or list of symbols for multiple transitions)
            stack_symbol: Symbol to pop from stack ('' for no pop)
            stack_push: List of symbols to push onto stack (empty for no push)
            by: Whether to use state names or IDs
        """
        if isinstance(symbol, list):
            for sym in symbol:
                if sym not in self.alphabet and sym != "":
                    self.alphabet.add(sym)

                source_state, target_state = self._get_source_and_target(by, source, target)

                # Add stack symbols to stack alphabet
                self.stack_alphabet.add(stack_symbol)
                self.stack_alphabet.update(stack_push)

                transition = PDATransition(sym, source_state, target_state,
                                           stack_symbol, stack_push)

                # Ensure determinism - only one transition per (input symbol, stack symbol) pair
                key = (sym, stack_symbol)
                if key in source_state.transitions:
                    raise ValueError(f"Duplicate transition for input '{sym}' and stack symbol '{stack_symbol}'")

                source_state.transitions[key] = transition
                source_state.used_symbols.add(sym)

        else:
            if symbol not in self.alphabet and symbol != "":
                self.alphabet.add(symbol)

            source_state, target_state = self._get_source_and_target(by, source, target)

            # Add stack symbols to stack alphabet
            self.stack_alphabet.add(stack_symbol)
            self.stack_alphabet.update(stack_push)

            transition = PDATransition(symbol, source_state, target_state,
                                       stack_symbol, stack_push)

            # Ensure determinism - only one transition per (input symbol, stack symbol) pair
            key = (symbol, stack_symbol)
            if key in source_state.transitions:
                raise ValueError(f"Duplicate transition for input '{symbol}' and stack symbol '{stack_symbol}' at state '{source_state.name}'")

            source_state.transitions[key] = transition
            source_state.used_symbols.add(symbol)

    def follow_epsilon_transitions(self):
        """Follow all possible epsilon transitions from current state"""
        while True:
            stack_top = self.stack[-1] if self.stack else '|'
            epsilon_transition = self.current_state.transitions.get(('', stack_top))

            if not epsilon_transition:
                break

            # Perform stack operations for epsilon transition
            if epsilon_transition.stack_symbol != '':  # If we need to pop
                if not self.stack or self.stack[-1] != epsilon_transition.stack_symbol:
                    break
                self.stack.pop()

            # Push new symbols in reverse order
            for push_symbol in reversed(epsilon_transition.stack_push):
                self.stack.append(push_symbol)

            self.current_state = epsilon_transition.target

    def process_input(self, simulation_input: str, require_empty_stack=None) -> bool:
        """
        Process input string and return whether it's accepted

        Args:
            simulation_input: String to process
            require_empty_stack: Override default empty stack requirement
        """

        print(f"Starting process with input: {simulation_input}")
        self.stack = self.initial_stack  # Reset stack to initial state
        self.current_state = self.initial_state  # Reset to initial state
        input_pos = 0  # Track position in input string

        # Use method parameter if provided, otherwise use class setting
        check_empty_stack = (require_empty_stack
                             if require_empty_stack is not None
                             else self.require_empty_stack)

        print(
            f"Initial state: {self.current_state.name}, Stack: {self.stack}, Require empty stack: {check_empty_stack}")

        # Follow initial epsilon transitions
        self.follow_epsilon_transitions()
        print(f"State after initial epsilon transitions: {self.current_state.name}, Stack: {self.stack}")

        while input_pos < len(simulation_input):
            symbol = simulation_input[input_pos]
            print(f"Processing symbol: '{symbol}' at position {input_pos}")

            if symbol not in self.alphabet:
                print(f"Symbol '{symbol}' not in alphabet. Rejecting input.")
                return False

            # Try to find a valid transition
            stack_top = self.stack[-1] if self.stack else '|'
            print(f"Top of stack: '{stack_top}'")

            transition = self.current_state.transitions.get((symbol, stack_top))
            if not transition:
                print(f"No transition found for (symbol: '{symbol}', stack_top: '{stack_top}'). Rejecting input.")
                return False

            print(f"Transition found: {transition}. Moving to state: {transition.target.name}")

            # Perform stack operations
            if transition.stack_symbol != '':  # If we need to pop
                if not self.stack or self.stack[-1] != transition.stack_symbol:
                    print(
                        f"Stack top '{self.stack[-1] if self.stack else None}' does not match required symbol '{transition.stack_symbol}'. Rejecting input.")
                    return False
                print(f"Popping stack top: '{self.stack.pop()}'")

            # Push new symbols in reverse order
            for push_symbol in reversed(transition.stack_push):
                self.stack.append(push_symbol)
                print(f"Pushed '{push_symbol}' onto stack. New stack: {self.stack}")

            self.current_state = transition.target
            input_pos += 1  # Move to next input symbol

            # Follow any epsilon transitions after processing input symbol
            self.follow_epsilon_transitions()
            print(f"State after epsilon transitions: {self.current_state.name}, Stack: {self.stack}")

        # Follow any remaining epsilon transitions after input is consumed
        self.follow_epsilon_transitions()
        print(f"Final state after input: {self.current_state.name}, Stack: {self.stack}")

        # Accept if:
        # 1. All input was consumed (input_pos == len(simulation_input))
        # 2. In a final state
        # 3. Stack is empty (if required)
        acceptance = (input_pos == len(simulation_input) and
                      self.current_state.is_final and
                      (not check_empty_stack or len(self.stack) == 1))
        print(f"Acceptance criteria: Input consumed={input_pos == len(simulation_input)}, "
              f"Final state={self.current_state.is_final}, "
              f"Stack empty={len(self.stack) == 1 if check_empty_stack else 'N/A'}")
        print(f"Result: {'Accepted' if acceptance else 'Rejected'}")

        return acceptance


class NPDA(Automaton):
    def __init__(self, name='NPDA', description='', require_empty_stack=False):
        super().__init__(name, description, 'NPDA')
        self.initial_stack: List[str] = ['|']  # Initialize with bottom marker
        self.stack: List[str] = self.initial_stack.copy()  # Initialize with bottom marker
        self.stack_alphabet: Set[str] = {'|'}  # Initialize with bottom marker
        self.require_empty_stack = require_empty_stack
        self.current_states: Set[Tuple[State, Tuple[str, ...]]] = set()

    def add_transition(self, source: str, target: str, symbol: Union[str, List[str]],
                       stack_symbol: str, stack_push: List[str], by=By.NAME) -> None:
        if isinstance(symbol, list):
            for sym in symbol:
                self._add_single_transition(source, target, sym, stack_symbol, stack_push, by)
        else:
            self._add_single_transition(source, target, symbol, stack_symbol, stack_push, by)

    def _add_single_transition(self, source: str, target: str, symbol: str,
                               stack_symbol: str, stack_push: List[str], by=By.NAME) -> None:
        if symbol not in self.alphabet and symbol != "":
            self.alphabet.add(symbol)

        source_state, target_state = self._get_source_and_target(by, source, target)

        self.stack_alphabet.add(stack_symbol)
        self.stack_alphabet.update(stack_push)

        transition = PDATransition(symbol, source_state, target_state,
                                   stack_symbol, stack_push)

        if symbol not in source_state.transitions:
            source_state.transitions[symbol] = []
        source_state.transitions[symbol].append(transition)
        source_state.used_symbols.add(symbol)

    def _apply_stack_operation(self, stack: List[str],
                               stack_symbol: str, stack_push: List[str]) -> Union[List[str], None]:
        if stack_symbol and (not stack or stack[-1] != stack_symbol):
            return None

        new_stack = stack[:-1] if stack_symbol else stack.copy()

        for symbol in reversed(stack_push):
            new_stack.append(symbol)

        return new_stack

    def _get_epsilon_closure(self, state: State, stack: List[str]) -> Set[Tuple[State, Tuple[str, ...]]]:
        closure = {(state, tuple(stack))}
        stack_states_to_process = [(state, stack)]

        while stack_states_to_process:
            current_state, current_stack = stack_states_to_process.pop()

            if "" in current_state.transitions:
                for transition in current_state.transitions[""]:
                    new_stack = self._apply_stack_operation(
                        current_stack.copy(),
                        transition.stack_symbol,
                        transition.stack_push
                    )

                    if new_stack is not None:
                        new_config = (transition.target, tuple(new_stack))
                        if new_config not in closure:
                            closure.add(new_config)
                            stack_states_to_process.append((transition.target, new_stack))

        return closure

    def process_input(self, simulation_input: str, require_empty_stack=None) -> bool:
        check_empty_stack = (require_empty_stack
                             if require_empty_stack is not None
                             else self.require_empty_stack)

        self.current_states = self._get_epsilon_closure(self.initial_state, self.initial_stack.copy())

        for symbol in simulation_input:
            if symbol not in self.alphabet:
                return False

            next_states = set()

            for current_state, current_stack in self.current_states:
                if symbol in current_state.transitions:
                    for transition in current_state.transitions[symbol]:
                        new_stack = self._apply_stack_operation(
                            list(current_stack),
                            transition.stack_symbol,
                            transition.stack_push
                        )

                        if new_stack is not None:
                            next_states.update(
                                self._get_epsilon_closure(transition.target, new_stack)
                            )

            if not next_states:
                return False

            self.current_states = next_states

        return any(
            state.is_final and (not check_empty_stack or len(stack) == 1)
            for state, stack in self.current_states
        )
