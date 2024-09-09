"""
NFA example

Checks if a binary number is even

Example using input string 'a, b'

If alphabet has multichar symbols, use input list instead
"""
from automata.nfa import NFA

# Create a NFA object
nfa = NFA()

# Define the alphabet
# Technically not necessary, since the alphabet is inferred from transitions
nfa.alphabet = ('a', 'b')

# Add states to the NFA
nfa.add_state('q0')
nfa.add_state('q1')
nfa.add_state('q2', is_final=True)

# Add transitions to the NFA
nfa.add_epsilon_transition('q0', 'q1')
nfa.add_transition('q0', 'a', 'q1')
nfa.add_epsilon_transition('q0', 'q2')

input_list = ['a', 'b']
input_string = ''

# Process input
result = nfa.process_input(input_string)
print(result)



