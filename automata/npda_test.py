from typing import Set, Tuple, List, Union
from automata.automaton import Automaton
from automata.state import State, By
from automata.transition import PDATransition


class NPDA(Automaton):
    def __init__(self, name='NPDA', description='', require_empty_stack=False):
        super().__init__(name, description, 'NPDA')
        self.initial_stack: List[str] = ['|']  # Initialize with bottom marker
        self.stack: List[str] = self.initial_stack.copy()  # Initialize with bottom marker
        self.stack_alphabet: Set[str] = {'|'}  # Initialize with bottom marker
        self.require_empty_stack = require_empty_stack
        self.current_states: Set[Tuple[State, Tuple[str, ...]]] = set()
        print(f"[INIT] NPDA initialized with name: {name}, require_empty_stack: {require_empty_stack}")

    def add_transition(self, source: str, target: str, symbol: Union[str, List[str]],
                       stack_symbol: str, stack_push: List[str], by=By.NAME) -> None:
        if isinstance(symbol, list):
            for sym in symbol:
                self._add_single_transition(source, target, sym, stack_symbol, stack_push, by)
        else:
            self._add_single_transition(source, target, symbol, stack_symbol, stack_push, by)
        print(
            f"[ADD_TRANSITION] Added transition from {source} to {target} on symbol(s) {symbol} with stack pop '{stack_symbol}' and push {stack_push}")

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
        print(
            f"[ADD_SINGLE_TRANSITION] Added transition from {source} to {target} on symbol '{symbol}' with stack pop '{stack_symbol}' and push {stack_push}")

    def _apply_stack_operation(self, stack: List[str],
                               stack_symbol: str, stack_push: List[str]) -> Union[List[str], None]:
        print(f"[APPLY_STACK_OPERATION] Current stack: {stack}, stack pop: '{stack_symbol}', stack push: {stack_push}")

        # If we need to pop but either stack is empty or top doesn't match
        if stack_symbol and (not stack or stack[-1] != stack_symbol):
            print(
                f"[APPLY_STACK_OPERATION] Stack pop failed - needed '{stack_symbol}' but stack top was '{stack[-1] if stack else 'empty'}'")
            return None

        # Create new stack: remove top element if we need to pop
        new_stack = stack[:-1] if stack_symbol else stack.copy()

        # Push new symbols in reverse order
        for symbol in reversed(stack_push):
            new_stack.append(symbol)

        print(f"[APPLY_STACK_OPERATION] New stack after operation: {new_stack}")
        return new_stack

    def _get_epsilon_closure(self, state: State, stack: List[str]) -> Set[Tuple[State, Tuple[str, ...]]]:
        closure = {(state, tuple(stack))}
        stack_states_to_process = [(state, stack)]

        while stack_states_to_process:
            current_state, current_stack = stack_states_to_process.pop()

            # Get epsilon transitions
            if "" in current_state.transitions:
                for transition in current_state.transitions[""]:
                    # Try to apply the stack operation
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

        print(f"[EPSILON_CLOSURE] Computed epsilon closure: {closure}")
        return closure

    def process_input(self, simulation_input: str, require_empty_stack=None) -> bool:
        check_empty_stack = (require_empty_stack
                             if require_empty_stack is not None
                             else self.require_empty_stack)

        # Start with epsilon closure of initial state
        self.current_states = self._get_epsilon_closure(self.initial_state, self.initial_stack.copy())
        print(f"[PROCESS_INPUT] Initial states after epsilon closure: {self.current_states}")

        # Process each input symbol
        for symbol in simulation_input:
            if symbol not in self.alphabet:
                print(f"[PROCESS_INPUT] Input symbol '{symbol}' not in alphabet")
                return False

            next_states = set()
            print(f"[PROCESS_INPUT] Processing symbol: '{symbol}'")

            # For each current configuration
            for current_state, current_stack in self.current_states:
                # Check if we have transitions for this input symbol
                if symbol in current_state.transitions:
                    # Try each transition
                    for transition in current_state.transitions[symbol]:
                        new_stack = self._apply_stack_operation(
                            list(current_stack),
                            transition.stack_symbol,
                            transition.stack_push
                        )

                        if new_stack is not None:
                            # Get epsilon closure of new configuration
                            next_states.update(
                                self._get_epsilon_closure(transition.target, new_stack)
                            )

            if not next_states:
                print(f"[PROCESS_INPUT] No valid transitions found for symbol '{symbol}', rejecting input.")
                return False

            self.current_states = next_states
            print(f"[PROCESS_INPUT] Current states after processing symbol '{symbol}': {self.current_states}")

        # Check acceptance conditions
        result = any(
            state.is_final and (not check_empty_stack or len(stack) == 1)
            for state, stack in self.current_states
        )
        print(f"[PROCESS_INPUT] Final result: {'Accepted' if result else 'Rejected'}")
        return result