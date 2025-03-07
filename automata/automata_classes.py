from inspect import stack
from typing import List, Set, Tuple, Union, Callable, Dict, Any

from PIL.Image import composite

from automata.automaton import Automaton
from automata.state import By, State
from automata.transition import PDATransition, Transition, MappingType, TuringTransition, MultiStackPDATransition


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
    def __init__(self, name='NFA', description=''):
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
    def __init__(self, name='DPDA', description='', initial_stack=None, require_empty_stack=False):
        super().__init__(name, description, 'DPDA')
        if initial_stack is None:
            self.initial_stack: List[str] = ['|']  # Initialize with bottom marker
        else:
            self.initial_stack: List[str] = initial_stack
        self.stack: List[str] = self.initial_stack
        self.stack_alphabet: Set[str] = set(self.initial_stack)  # Initialize with bottom marker
        self.require_empty_stack = require_empty_stack

    def add_transition(self, source: str, target: str, symbol: Union[List[str], str],
            stack_symbol: Union[List[str], str], stack_push: Union[List[str],
            Tuple[Callable[..., any], Union[int, dict]]], by: By=By.NAME,
            mapping_type: MappingType = MappingType.ONE_TO_ONE) -> None:
        """
        Add a transition for DPDA

        Args:
            source: Source state name/id
            target: Target state name/id
            symbol: Input symbol (str for a single symbol or list of symbols for multiple transitions)
            stack_symbol: Symbol to pop from stack ('' for no pop)
            stack_push: List of symbols to push onto stack (empty for no push)
            by: Whether to use state names or IDs
            :param stack_symbol:
            :param by:
            :param stack_push:
            :param symbol:
            :param target:
            :param source:
            :param mapping_type:
        """
        if isinstance(stack_symbol, str):
            if stack_symbol == "":
                raise ValueError("Empty stack symbol not allowed in PDA transitions")
        elif any(symbol == "" for symbol in stack_symbol):
            raise ValueError("Empty stack symbol not allowed in PDA transitions")

        if isinstance(symbol, list) or isinstance(stack_symbol, list):
            if mapping_type == MappingType.ALL_TO_ALL:
                # All-to-All mapping: Create transitions for every combination
                for sym in symbol:
                    for stack_sym in stack_symbol:
                        self._add_single_transition(source, target, sym, stack_sym, stack_push, by)

            elif mapping_type == MappingType.ONE_TO_ONE:
                # One-to-One mapping: Only valid if both lists are of the same length
                if len(symbol) != len(stack_symbol):
                    raise ValueError("symbol and stack_symbol lists must be of the same length for ONE_TO_ONE mapping")

                for sym, stack_sym in zip(symbol, stack_symbol):
                    self._add_single_transition(source, target, sym, stack_sym, stack_push, by)
        else:
            # Handle cases where symbol or stack_symbol is a single item
            if not isinstance(symbol, list):
                symbol = [symbol]
            if not isinstance(stack_symbol, list):
                stack_symbol = [stack_symbol]

            for sym in symbol:
                for stack_sym in stack_symbol:
                    self._add_single_transition(source, target, sym, stack_sym, stack_push, by)

    def _add_single_transition(self, source: str, target: str, symbol: str, stack_symbol: str,
            stack_push: Union[List[str], Tuple[Callable[..., any]], Union[int, dict]], by=By.NAME) -> None:
        if symbol not in self.alphabet and symbol != "":
            self.alphabet.add(symbol)

        source_state, target_state = self._get_source_and_target(by, source, target)

        if symbol == "" and source_state.transitions:
            raise ValueError("Epsilon transition cannot be added to a state with existing transitions")

        self.stack_alphabet.add(stack_symbol)

        if isinstance(stack_push, list):
            # Add stack symbols to stack alphabet
            self.stack_alphabet.update(stack_push)

            transition = PDATransition(symbol, source_state, target_state,
                                       stack_symbol, stack_push)
        elif isinstance(stack_push[0], Callable):
            stack_push, repeat = stack_push[0], stack_push[1]
            stack_push = stack_push(repeat, symbol, stack_symbol)

            self.stack_alphabet.update(stack_push)

            transition = PDATransition(symbol, source_state, target_state,
                                       stack_symbol, stack_push)
        else:
            raise ValueError("Invalid stack_push argument. Must be a list of symbols or a Push object")


        # Ensure determinism - only one transition per (input symbol, stack symbol) pair
        key = (symbol, stack_symbol)
        if key in source_state.transitions:
            raise ValueError(f"Duplicate transition for input '{symbol}' and stack symbol '{stack_symbol}'")

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

        self.stack = self.initial_stack  # Reset stack to initial state
        self.current_state = self.initial_state  # Reset to initial state
        input_pos = 0  # Track position in input string

        # Use method parameter if provided, otherwise use class setting
        check_empty_stack = (require_empty_stack
                             if require_empty_stack is not None
                             else self.require_empty_stack)

        # Follow initial epsilon transitions
        self.follow_epsilon_transitions()

        while input_pos < len(simulation_input):
            symbol = simulation_input[input_pos]

            if symbol not in self.alphabet:
                return False

            # Try to find a valid transition
            stack_top = self.stack[-1] if self.stack else '|'

            transition = self.current_state.transitions.get((symbol, stack_top))
            if not transition:
                return False

            # Perform stack operations
            if not self.stack or self.stack[-1] != transition.stack_symbol:
                return False

            self.stack.pop()

            # Push new symbols in reverse order
            for push_symbol in reversed(transition.stack_push):
                self.stack.append(push_symbol)

            self.current_state = transition.target
            input_pos += 1  # Move to next input symbol

            # Follow any epsilon transitions after processing input symbol
            self.follow_epsilon_transitions()

        # Follow any remaining epsilon transitions after input is consumed
        self.follow_epsilon_transitions()

        # Accept if:
        # 1. All input was consumed (input_pos == len(simulation_input))
        # 2. In a final state
        # 3. Stack is empty (if required)
        acceptance = (input_pos == len(simulation_input) and
                      self.current_state.is_final and
                      (not check_empty_stack or len(self.stack) == 1))

        self.output[simulation_input] = {
            "state": self.current_state.name,
            "accepted": acceptance
        }
        return acceptance


class NPDA(Automaton):
    def __init__(self, name='NPDA', description='', initial_stack=None, require_empty_stack=False):
        super().__init__(name, description, 'NPDA')
        if initial_stack is None:
            self.initial_stack = ['|'] # Initialize with bottom marker
        else:
            self.initial_stack: List[str] = initial_stack # Initialize custom initial stack
        self.stack: List[str] = self.initial_stack.copy()
        self.stack_alphabet: Set[str] = set(self.initial_stack)  # Initialize with bottom marker
        self.require_empty_stack = require_empty_stack
        self.current_states: Set[Tuple[State, Tuple[str, ...]]] = set()

    def add_transition(self, source: str, target: str, symbol: Union[str, List[str]],
                       stack_symbol: Union[str, List[str]], stack_push: Union[List[str],
            Tuple[Callable[..., any], Union[int, dict]]], by=By.NAME,
                       mapping_type: MappingType=MappingType.ONE_TO_ONE) -> None:
        if isinstance(stack_symbol, str):
            if stack_symbol == "":
                raise ValueError("Empty stack symbol not allowed in PDA transitions")
        elif any(symbol == "" for symbol in stack_symbol):
            raise ValueError("Empty stack symbol not allowed in PDA transitions")

        if isinstance(symbol, list) or isinstance(stack_symbol, list):
            if mapping_type == MappingType.ALL_TO_ALL:
                # All-to-All mapping: Create transitions for every combination
                for sym in symbol:
                    for stack_sym in stack_symbol:
                        self._add_single_transition(source, target, sym, stack_sym, stack_push, by)

            elif mapping_type == MappingType.ONE_TO_ONE:
                # One-to-One mapping: Only valid if both lists are of the same length
                if len(symbol) != len(stack_symbol):
                    raise ValueError("symbol and stack_symbol lists must be of the same length for ONE_TO_ONE mapping")

                for sym, stack_sym in zip(symbol, stack_symbol):
                    self._add_single_transition(source, target, sym, stack_sym, stack_push, by)
        else:
            # Handle cases where symbol or stack_symbol is a single item
            if not isinstance(symbol, list):
                symbol = [symbol]
            if not isinstance(stack_symbol, list):
                stack_symbol = [stack_symbol]

            for sym in symbol:
                for stack_sym in stack_symbol:
                    self._add_single_transition(source, target, sym, stack_sym, stack_push, by)

    def _add_single_transition(self, source: str, target: str, symbol: str,
                               stack_symbol: str, stack_push: Union[List[str], Tuple[Callable[..., any]], Union[int, dict]]
                               , by=By.NAME) -> None:
        if symbol not in self.alphabet and symbol != "":
            self.alphabet.add(symbol)

        source_state, target_state = self._get_source_and_target(by, source, target)

        self.stack_alphabet.add(stack_symbol)

        if isinstance(stack_push, list):
            self.stack_alphabet.update(stack_push)

            transition = PDATransition(symbol, source_state, target_state,
                                       stack_symbol, stack_push)

        elif isinstance(stack_push[0], Callable):
            stack_push, repeat = stack_push[0], stack_push[1]
            stack_push = stack_push(repeat, symbol, stack_symbol)

            self.stack_alphabet.update(stack_push)

            transition = PDATransition(symbol, source_state, target_state,
                                       stack_symbol, stack_push)
        else:
            raise ValueError("Invalid stack_push argument. Must be an empty list or a list of symbols or a Push object")


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

        acceptance = any(
            state.is_final and (not check_empty_stack or len(stack) == 1)
            for state, stack in self.current_states
        )

        self.output[simulation_input] = {
            "states": [state.name for state, _ in self.current_states],
            "accepted": acceptance
        }
        return acceptance


class Turing(Automaton):
    def __init__(self, name='Turing Machine', description='', blank_symbol='|'):
        super().__init__(name, description, 'Turing')
        self.tape = []
        self.head_position = 1
        self.blank_symbol = blank_symbol

    def add_transition(self, source: str, target: str, tape_symbol: Union[str, List[str]],
                       tape_write: Union[str, List[str]], move: str, by=By.NAME,
                       mapping_type: MappingType=MappingType.ONE_TO_ONE) -> None:
        if isinstance(tape_symbol, list) and isinstance(tape_write, list):
            if mapping_type == MappingType.ALL_TO_ALL:
                # All-to-All mapping: Create transitions for every combination
                for sym in tape_symbol:
                    for write in tape_write:
                        self._add_single_transition(source, target, sym, write, move, by)
            elif mapping_type == MappingType.ONE_TO_ONE:
                # One-to-One mapping: Only valid if both lists are of the same length
                if len(tape_symbol) != len(tape_write):
                    raise ValueError("tape_symbol and tape_write lists must be of the same length for ONE_TO_ONE mapping")
                for sym, write in zip(tape_symbol, tape_write):
                    self._add_single_transition(source, target, sym, write, move, by)

        else:
            # Handle cases where tape_symbol or tape_write is a single item
            if not isinstance(tape_symbol, list):
                tape_symbol = [tape_symbol]
            if not isinstance(tape_write, list):
                tape_write = [tape_write]

            for sym in tape_symbol:
                for write in tape_write:
                    self._add_single_transition(source, target, sym, write, move, by)

    def _add_single_transition(self, source: str, target: str, tape_symbol: str,
                               tape_write: str, move: str, by=By.NAME) -> None:
        if tape_symbol not in self.stack_alphabet and tape_symbol != "":
            self.stack_alphabet.add(tape_symbol)
        if tape_write not in self.stack_alphabet and tape_write != "":
            self.stack_alphabet.add(tape_write)

        source_state, target_state = self._get_source_and_target(by, source, target)

        if tape_symbol in source_state.transitions:
            raise ValueError(f"Duplicate transition for input '{tape_symbol}'")

        transition = TuringTransition(source_state, target_state, tape_symbol, tape_write, move)

        source_state.transitions[tape_symbol] = transition
        source_state.used_symbols.add(tape_symbol)

    def loop(self, source:str, tape_symbol:str, move:str, by=By.NAME):
        self.add_transition(source, source, tape_symbol, tape_symbol, move, by)

    def loop_right(self, source:str, tape_symbol:str, by=By.NAME):
        self.add_transition(source, source, tape_symbol, tape_symbol, 'R', by)

    def loop_left(self, source:str, tape_symbol:str, by=By.NAME):
        self.add_transition(source, source, tape_symbol, tape_symbol, 'L', by)

    def process_input(self, simulation_input: Union[List[str], str]) -> tuple[bool, list[str]]:
        self.tape = list(self.blank_symbol) + list(simulation_input) + list(self.blank_symbol)
        self.head_position = 1

        iteration = 0
        while True:

            if iteration > 1000:
                return False, self.tape
            tape_symbol = self.tape[self.head_position]
            transition = self.current_state.transitions.get(tape_symbol)

            if not transition:
                return self.current_state.is_final, self.tape

            self.tape[self.head_position] = transition.tape_write
            self.head_position += 1 if transition.move == 'R' else -1 if transition.move == 'L' else 0

            if self.head_position < 0:
                self.tape.insert(0, self.blank_symbol)
                self.head_position = 0
            elif self.head_position >= len(self.tape):
                self.tape.append(self.blank_symbol)

            self.current_state = transition.target
            iteration += 1


class MultiStackPDA(Automaton):
    def __init__(self, stack_amount=2, name='Multi-Stack PDA', deterministic=True, initial_stacks: List[List[str]]=None, description='', require_empty_stack=False):
        super().__init__(name, description, 'MSPDA')
        if initial_stacks is None:
            self.initial_stacks: List[List[str]] = [['|'] for _ in range(stack_amount)]
        else:
            if len(initial_stacks) != stack_amount:
                raise ValueError("Number of initial stacks does not match stack_amount")
            self.initial_stacks: List[List[str]] = initial_stacks
        self.stacks: List[List[str]] = [stack.copy() for stack in self.initial_stacks]
        self.stack_alphabet: Set[str] = set([symbol for stack in self.initial_stacks for symbol in stack])
        self.deterministic = deterministic
        self.stack_amount = stack_amount
        self.stack_names = [f"stack_{i}" for i in range(stack_amount)]
        if not self.deterministic:
            self.current_state = None


class MultiTapeTuring(Automaton):
    def __init__(self, name='Multi-Tape Turing Machine', description='', blank_symbol='|'):
        super().__init__(name, description, 'Multi-Tape Turing')
        self.tapes = []
        self.head_positions = [1]
        self.blank_symbol = blank_symbol