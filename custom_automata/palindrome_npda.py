from automata.automata_classes import NPDA
from automata.serialize.serialize_flaci import export_to_flaci
from automata.state import By

# Initialize NPDA
NKA = NPDA("PalindromeNKA", "Checks if input string is case-sensitive palindrome")

# Define alphabet with both lowercase and uppercase letters
x = {"a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w",
     "x", "y", "z",
     "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W",
     "X", "Y", "Z"}

NKA.alphabet = x
NKA.stack_alphabet = {'|'} | {char for char in x}
NKA.initial_stack = ['|']

# Add states
NKA.add_state("q0", "1", False, "")
NKA.add_state("q1", "2", False, "")
NKA.add_state("q2", "3", True, "")

# Add transitions for all characters
for char in x:
    # First state transitions with empty stack (pushing character onto stack)
    NKA.add_transition("1", "1", char, "|", [char, '|'], By.ID)

    # First state transitions with characters on stack (pushing new character)
    for stack_char in x:
        NKA.add_transition("1", "1", char, stack_char, [char, stack_char], By.ID)

    # Transitions from first to second state (epsilon transitions)
    NKA.add_transition("1", "2", "", char, [char], By.ID)  # Keep one character
    NKA.add_transition("1", "2", "", char, [], By.ID)  # Remove character

    # Second state transitions (popping matching characters)
    NKA.add_transition("2", "2", char, char, [], By.ID)

# Final transition to accepting state
NKA.add_transition("2", "3", "", "|", ['|'], By.ID)

print(NKA.process_input("RelieffeileS"))  # Should print True

export_to_flaci(NKA)