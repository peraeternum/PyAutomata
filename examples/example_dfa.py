from automata.dfa import DFA

"""
DFA example

Checks if a binary number is even

Example using input string '101010'

If alphabet has multichar symbols, use input list instead
"""

# Create a DFA object
dfa = DFA()

# Define the alphabet
# Technically not necessary, since the alphabet is inferred from transitions
dfa.alphabet = {'0', '1', '2'}

# Add states to the DFA
dfa.add_state('q0', is_final=True)
dfa.add_state('q1')

# Add transitions to the DFA
dfa.add_transition('q0', '0', 'q0')
dfa.add_transition('q0', '1', 'q1')
dfa.add_transition('q1', '0', 'q0')
dfa.add_transition('q1', '1', 'q1')

# Set the initial state of the DFA
# Not necessary in this case, since the first state added is the initial state
dfa.set_initial_state('q0')

# Define input
input_string = '101010'

# Other test inputs:
test = '101011'
test2 = '1010100'
test3 = ['1', '0', '1', '0', '0', '0']
test4 = ['1', '0', '1', '0', '1', '1']

# Process input
result = dfa.process_input(test2)
print(f"Result: {result}")
