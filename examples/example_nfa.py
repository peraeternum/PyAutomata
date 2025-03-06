# Initialize the NFA
from automata.automata_classes import NFA

nfa = NFA()

# Define the alphabet (optional, inferred from transitions)
nfa.alphabet = ('a', 'b')

# Add states
nfa.add_state('q0')          # Start state
nfa.add_state('q1')          # Intermediate state when 'a' is found
nfa.add_state('q2', is_final=True)  # Final state when "ab" is found

# Define transitions
nfa.add_transition('q0', 'q0', 'a')  # Loop on 'a' in the start state to allow preceding 'a's
nfa.add_transition('q0', 'q0', 'b')  # Loop on 'b' in the start state
nfa.add_transition('q0', 'q1', 'a')  # Transition to 'q1' upon seeing 'a' for the first time
nfa.add_transition('q1', 'q2', 'b')  # Transition to final state 'q2' upon seeing 'b' after 'a'
nfa.add_transition('q2', 'q2', 'a')  # Allow further 'a's in final state
nfa.add_transition('q2', 'q2', 'b')  # Allow further 'b's in final state

# Test the NFA with some inputs
input_strings = ["ab", "aab", "bbaab", "aabb", "ba"]
for input_string in input_strings:
    result = nfa.process_input(input_string)
    print(f"Input '{input_string}' accepted? {result}")
