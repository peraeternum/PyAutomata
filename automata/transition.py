from dataclasses import dataclass
from enum import Enum
from typing import List, Union, Callable, Tuple, Dict

from automata.state import State


class Transition:
    def __init__(self, symbol, source, target, x=0, y=0):
        self.symbol = symbol
        self.source = source
        self.target = target
        self.x = x
        self.y = y

class MealyTransition(Transition):
    def __init__(self, symbol, source, target, output, x=0, y=0):
        super().__init__(symbol, source, target, x, y)
        self.output = output # Only used by Mealy machines


@dataclass
class PDATransition(Transition):
    """Transition class for PDAs with stack operations"""
    stack_symbol: str  # Symbol to read from stack
    stack_push: List[str]  # Symbols to push onto stack (an empty list means no push)

    def __init__(self, symbol: str, source: 'State', target: 'State',
                 stack_symbol: str, stack_push: List[str], x: int = 0, y: int = 0):
        super().__init__(symbol, source, target, x, y)
        self.stack_symbol = stack_symbol
        self.stack_push = stack_push


@dataclass
class TuringTransition(Transition):
    """Transition class for Turing machines"""
    tape_symbol: str  # Symbol to read from tape
    tape_write: str  # Symbol to write to tape
    move: str  # Move tape head (L, R, or N for None)

    def __init__(self, source: 'State', target: 'State',
                 tape_symbol: str, tape_write: str, move: str, x: int = 0, y: int = 0):
        super().__init__(tape_symbol, source, target, x, y)
        self.tape_symbol = tape_symbol
        self.tape_write = tape_write
        self.move = move


@dataclass
class MultiStackPDATransition(Transition):
    """Transition class for PDAs with multiple stack operations"""
    stack_operations: Dict[str, List[str]]

    def __init__(self, symbol: str, source: 'State', target: 'State',
                 stack_operations: Dict,
                 x: int = 0, y: int = 0):
        """
        Initialize a multi-stack PDA transition

        Args:
            symbol: Input symbol triggering the transition
            source: Source state
            target: Target state
            stack_symbols: Dict[stack_name, pop_symbol] or List[List[pop_symbols]]
            stack_pushes: Dict[stack_name, push_symbols] or List[List[push_symbols]]
            x: X coordinate for visualization (optional)
            y: Y coordinate for visualization (optional)
        """
        super().__init__(symbol, source, target, x, y)



class Push:
    """
    Class representing a push operation in a PDA transition
    Makes more complex push operations easier to handle and create
    """

    def __init__(self):
        self._stack_push = None

    def reversed(self, repeat=1)-> Tuple[Callable[..., any], Union[int, dict]]:
        return self._reversed, repeat

    def _reversed(self, repeat, symbols, stack_symbols):
        if isinstance(repeat, int):
            self._stack_push = (list(symbols) + list(stack_symbols))[::-1]
            return self._stack_push * repeat
        elif isinstance(repeat, dict):
            pass # dict functionality not implemented yet
        else:
            raise ValueError("Invalid value for 'repeat' parameter. Expected int or dict.")

        return self._stack_push

    def sequential(self, repeat=1)-> Tuple[Callable[..., any], Union[int, dict]]:
        return self._sequential, repeat

    def _sequential(self, repeat, symbols, stack_symbols):
        if isinstance(repeat, int):
            self._stack_push = (list(symbols)+list(stack_symbols))*repeat
            return self._stack_push
        elif isinstance(repeat, dict):
            pass # dict functionality not implemented yet
        return self._stack_push

    def stack_symbol(self, repeat=1)-> Tuple[Callable[..., any], Union[int, dict]]:
        return self._stack_symbol, repeat

    def _stack_symbol(self, repeat, symbols, stack_symbols):
        if isinstance(repeat, int):
            self._stack_push = list(stack_symbols)*repeat
            return self._stack_push
        elif isinstance(repeat, dict):
            pass # dict functionality not implemented yet
        else:
            raise ValueError("Invalid value for 'repeat' parameter. Expected int or dict.")
        return self._stack_push

    def symbol(self, repeat=1)-> Tuple[Callable[..., any], Union[int, dict]]:
        return self._symbol, repeat

    def _symbol(self, repeat, symbols, stack_symbols):
        if isinstance(repeat, int):
            self._stack_push = list(symbols)*repeat
            return self._stack_push
        elif isinstance(repeat, dict):
            pass # dict functionality not implemented yet
        else:
            raise ValueError("Invalid value for 'repeat' parameter. Expected int or dict.")
        return self._stack_push


class MappingType(Enum):
    ALL_TO_ALL = "all_to_all"
    ONE_TO_ONE = "one_to_one"
    CUSTOM = "custom"  # For future extension if you want more control