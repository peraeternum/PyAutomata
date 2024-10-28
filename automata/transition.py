from dataclasses import dataclass
from typing import List

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
    stack_push: List[str]  # Symbols to push onto stack (empty list means no push)

    def __init__(self, symbol: str, source: 'State', target: 'State',
                 stack_symbol: str, stack_push: List[str], x: int = 0, y: int = 0):
        super().__init__(symbol, source, target, x, y)
        self.stack_symbol = stack_symbol
        self.stack_push = stack_push