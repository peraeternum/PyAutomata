from automata.automata_classes import NPDA
from automata.transition import Push, MappingType

# Initialize NPDA
NPDA = NPDA("PalindromeNKA", "Checks if input string is case-sensitive palindrome")
push = Push()

# Define alphabet with both lowercase and uppercase letters
x = {"a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w",
     "x", "y", "z",
     "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W",
     "X", "Y", "Z"}

NPDA.alphabet = x
NPDA.stack_alphabet = {'|'} | {char for char in x}
NPDA.initial_stack = ['|']

# Add states
NPDA.add_state("q0", "1", False, "")
NPDA.add_state("q1", "2", False, "")
NPDA.add_state("q2", "3", True, "")

# Add transitions for all characters
NPDA.add_transition("q0", "q0", list(x), "|", push.sequential(1))
NPDA.add_transition("q0", "q0", list(x), list(x), push.sequential(1), mapping_type=MappingType.ALL_TO_ALL)
NPDA.add_transition("q0", "q1", "", list(x), push.stack_symbol(1))
NPDA.add_transition("q0", "q1", "", list(x), [])
NPDA.add_transition("q1", "q1", list(x), list(x), [])
NPDA.add_transition("q1", "q2", "", "|", push.stack_symbol(1))

print(NPDA.process_input("RelieffeileS"))  # Should print True
