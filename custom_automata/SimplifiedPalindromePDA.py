from automata.automata_classes import DPDA
import string
from automata.transition import MappingType

from automata.transition import Push

# Create new DPDA instance
DPDA = DPDA("Palindrome", "")
Push = Push()

# Define alphabet as all uppercase and lowercase letters plus the middle marker $
alphabet_letters = set(string.ascii_letters)
DPDA.alphabet = alphabet_letters | {'$'}

# Define stack alphabet (all letters plus stack bottom marker)
DPDA.stack_alphabet = alphabet_letters | {'#'}

# Define initial stack
DPDA.initial_stack = ['#']

# Add states
DPDA.add_state("q0", "1", False, "")  # Initial state
DPDA.add_state("q1", "2", False, "")  # Middle state
DPDA.add_state("q2", "3", True, "")  # Final state

DPDA.add_transition("q0", "q0", list(alphabet_letters), "#", Push.sequential(1))
DPDA.add_transition("q0", "q0", list(alphabet_letters), list(alphabet_letters), Push.sequential(1), mapping_type=MappingType.ALL_TO_ALL)
DPDA.add_transition("q0", "q1", "$", list(alphabet_letters), Push.stack_symbol(1))
DPDA.add_transition("q0", "q1", "$", "#", Push.stack_symbol(1))
DPDA.add_transition("q1", "q1", list(alphabet_letters), list(alphabet_letters), [])
DPDA.add_transition("q1", "q2", "", "#", [])

print(DPDA.process_input("Relief$feileS"))  # Should print processing message and return True
