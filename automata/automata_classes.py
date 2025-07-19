"""
This module defines the high-level classes for various types of formal automata.

Each class inherits from the base `Automaton` class and implements the specific logic
for its type, such as how it processes input strings and what constitutes a valid
transition. These are the main classes intended for user interaction.
"""

from typing import List, Set, Tuple, Union, Callable

from automata.automaton import Automaton
from automata.state import By, State, AutomatonState
from automata.transition import PDATransition, Transition, MappingType, TuringTransition


class DFA(Automaton):
    """
        Represents a Deterministic Finite Automaton (DFA).

        A DFA is a finite-state machine that accepts or rejects strings of symbols.
        For each state and each symbol in the alphabet, there is exactly one
        transition to a next state.

        Attributes:
            name (str): The name of the DFA.
            description (str): A brief description of the DFA's purpose.
            allow_partial (bool): If True, allows the DFA to have states with
                                  undefined transitions for some symbols.
        """
    def __init__(self, name='DFA', description='', allow_partial=False):
        """
        Initializes a new DFA.

        Args:
            name (str, optional): The name of the automaton. Defaults to 'DFA'.
            description (str, optional): A description of the automaton. Defaults to ''.
            allow_partial (bool, optional): Whether to allow incomplete transition
                                            functions. If False, `check_automaton`
                                            will raise an error for missing transitions.
                                            Defaults to False.
        """
        super().__init__(name, description, 'DFA', allow_partial)

class MOORE(Automaton):
    def __init__(self, name='MOORE', description='', allow_partial=False):
        super().__init__(name, description, 'MOORE', allow_partial)

class MEALY(Automaton):
    def __init__(self, name='MEALY', description='', allow_partial=False):
        super().__init__(name, description,  'MEALY', allow_partial)


class NFA(Automaton):
    """
    Represents a Non-deterministic Finite Automaton (NFA).

    An NFA can have multiple possible next states for a given state and symbol,
    and can also have transitions on an empty input (ε-transitions). It accepts
    an input string if at least one possible path of execution leads to a final state.
    """
    def __init__(self, name='NFA', description=''):
        """
        Initializes a new NFA.

        Args:
            name (str, optional): The name of the automaton. Defaults to 'NFA'.
            description (str, optional): A description of the automaton. Defaults to ''.
        """
        super().__init__(name, description, 'NFA')

    # Add epsilon transitions for non-deterministic automata
    def add_epsilon_transition(self, source, target, by=By.NAME):
        """
        Adds an epsilon (ε) transition between two states.

        Args:
            source (str): The name or ID of the source state.
            target (str): The name or ID of the target state.
            by (By, optional): The attribute to use for identifying states
                               (By.NAME or By.ID). Defaults to By.NAME.
        """
        source_state, target_state = self._get_source_and_target(by, source, target)

        transition = Transition([""], source_state, target_state)

        # Epsilon transitions are stored separately for efficient closure calculation
        if "" not in source_state.transitions:
            source_state.transitions[""] = []
        source_state.transitions[""].append(transition)


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
        """
        Processes an input string and determines if the NFA accepts it.

        This method simulates the NFA's execution by tracking all possible
        current states. After consuming the entire string, it checks if any
        of the final states are in the set of possible current states.

        Args:
            simulation_input (str): The string to be processed by the NFA.

        Returns:
            bool: True if the string is accepted, False otherwise.
        """

        # Check if the NFA has any epsilon transitions
        has_epsilon_transitions = any(
            any(transition.symbol == '' for transitions in state.transitions.values()
                for transition in (transitions if isinstance(transitions, list) else [transitions]))
            for state in self.states.values()
        )

        # Start with the initial state and its epsilon closure if needed
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
    """
    Represents a Deterministic Pushdown Automaton (DPDA).

    A DPDA is a finite automaton equipped with a stack. It is deterministic,
    meaning for any given state, input symbol, and stack top symbol, there is
    at most one valid transition.

    Attributes:
        initial_stack (List[str]): The list of symbols on the stack at the start.
        require_empty_stack (bool): If True, the stack must be empty (or contain
                                    only the initial marker) for a string to be
                                    accepted, in addition to being in a final state.
    """
    def __init__(self, name='DPDA', description='', initial_stack=None, require_empty_stack=False):
        """
        Initializes a new DPDA.

        Args:
            name (str, optional): The name of the automaton. Defaults to 'DPDA'.
            description (str, optional): A description of the automaton. Defaults to ''.
            initial_stack (List[str], optional): The initial stack configuration.
                                                 Defaults to ['|'].
            require_empty_stack (bool, optional): Specifies if acceptance requires
                                                  an empty stack. Defaults to False.
        """
        super().__init__(name, description, 'DPDA')
        if initial_stack is None:
            self.initial_stack: List[str] = ['|']  # Initialize with a bottom marker
        else:
            self.initial_stack: List[str] = initial_stack
        self.stack: List[str] = self.initial_stack
        self.stack_alphabet: Set[str] = set(self.initial_stack)  # Initialize with a bottom marker
        self.require_empty_stack = require_empty_stack

    def add_transition(self, source: str, target: str, symbol: Union[List[str], str],
            stack_symbol: Union[List[str], str], stack_push: Union[List[str],
            Tuple[Callable[..., any], Union[int, dict]]], by: By=By.NAME,
            mapping_type: MappingType = MappingType.ONE_TO_ONE) -> None:
        """
        Adds a transition to the DPDA.

        For a DPDA, a transition is uniquely defined by the source state,
        input symbol, and the symbol at the top of the stack.

        Args:
            source (str): The name or ID of the source state.
            target (str): The name or ID of the target state.
            symbol (str): The input symbol for the transition. Use '' for an
                          epsilon (ε) transition.
            stack_symbol (str): The symbol that must be at the top of the stack
                                to take this transition.
            stack_push (List[str]): A list of symbols to push onto the stack.
                                    The symbols are pushed in order, so the last
                                    symbol in the list will be the new top.
                                    Use an empty list `[]` to signify a pop
                                    operation with no subsequent push.
            by (By, optional): The attribute to identify states by.
                               Defaults to By.NAME.
            mapping_type (MappingType, optional): How to handle multiple symbols.

        Raises:
            ValueError: If a transition for the given (symbol, stack_symbol)
                        pair already exists from the source state, which would
                        violate determinism.

        Example:
            # In state 'q1', on input 'a', if stack top is 'Z',
            # pop 'Z', push 'A' then 'Z', and go to 'q1'.
            dpda.add_transition('q1', 'q1', 'a', 'Z', ['A', 'Z'])
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
            # Handle cases where a symbol or stack_symbol is a single item
            if not isinstance(symbol, list):
                symbol = [symbol]
            if not isinstance(stack_symbol, list):
                stack_symbol = [stack_symbol]

            for sym in symbol:
                for stack_sym in stack_symbol:
                    self._add_single_transition(source, target, sym, stack_sym, stack_push, by)

    def _add_single_transition(self, source: str, target: str, symbol: str, stack_symbol: str,
            stack_push: Union[List[str], Tuple[Callable[..., any]], Union[int, dict]], by: By=By.NAME) -> None:
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
        """Follow all possible epsilon transitions from the current state"""
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
        Process an input string and return whether it's accepted

        Args:
            simulation_input: String to process
            require_empty_stack: Override default empty stack requirement
        """

        self.stack = self.initial_stack  # Reset stack to the initial state
        self.current_state = self.initial_state  # Reset to the initial state
        input_pos = 0  # Track position in the input string

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
            input_pos += 1  # Move to the next input symbol

            # Follow any epsilon transitions after processing the input symbol
            self.follow_epsilon_transitions()

        # Follow any remaining epsilon transitions after input is consumed
        self.follow_epsilon_transitions()

        # Accept if:
        # 1. All inputs were consumed (input_pos == len(simulation_input))
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
            self.initial_stack = ['|'] # Initialize with a bottom marker
        else:
            self.initial_stack: List[str] = initial_stack # Initialize custom initial stack
        self.stack: List[str] = self.initial_stack.copy()
        self.stack_alphabet: Set[str] = set(self.initial_stack)  # Initialize with a bottom marker
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
            # Handle cases where a symbol or stack_symbol is a single item
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

    @staticmethod
    def _apply_stack_operation(stack: List[str],
                               stack_symbol: str, stack_push: List[str]) -> Union[List[str], None]:
        if stack_symbol and (not stack or stack[-1] != stack_symbol):
            return None

        new_stack = stack[:-1] if stack_symbol else stack.copy()

        for symbol in reversed(stack_push):
            new_stack.append(symbol)

        return new_stack

    def _get_epsilon_closure(self, state: AutomatonState, stack: List[str]) -> Set[Tuple[AutomatonState, Tuple[str, ...]]]:
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

    def loop(self, source:str, tape_symbol:Union[list[str], str], move:str, by=By.NAME):
        self.add_transition(source, source, tape_symbol, tape_symbol, move, by)

    def loop_right(self, source:str, tape_symbol:Union[list[str], str], by=By.NAME):
        self.add_transition(source, source, tape_symbol, tape_symbol, 'R', by)

    def loop_left(self, source:str, tape_symbol:Union[list[str], str], by=By.NAME):
        self.add_transition(source, source, tape_symbol, tape_symbol, 'L', by)

    def process_input(
            self,
            simulation_input: Union[List[str], str],
            max_iterations=1000,
            return_steps=False
    ) -> Union[tuple[bool, list[str]], tuple[bool, list[str], int]]:
        self.current_state = self.initial_state
        self.tape = list(self.blank_symbol) + list(simulation_input) + list(self.blank_symbol)
        self.head_position = 1

        iteration = 0
        while True:
            if iteration > max_iterations:
                return False, self.tape
            tape_symbol = self.tape[self.head_position]
            transition = self.current_state.transitions.get(tape_symbol)
            if not transition:
                if return_steps:
                    if self.current_state.is_final:
                        return self.current_state.is_final, self.tape, iteration
                    else:
                        return self.current_state.is_final, self.tape, self.head_position
                if self.current_state.is_final:
                    return self.current_state.is_final, self.tape
                else:
                    return self.current_state.is_final, self.tape, self.head_position

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
        self.require_empty_stack = require_empty_stack

class MultiTapeTuring(Automaton):
    def __init__(self, name='Multi-Tape Turing Machine', description='', blank_symbol='|'):
        super().__init__(name, description, 'Multi-Tape Turing')
        self.tapes = []
        self.head_positions = [1]
        self.blank_symbol = blank_symbol