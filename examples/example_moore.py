from automata.automata_classes import MOORE

# Create a Moore machine
moore = MOORE('Even number of ones', 'Checks if there is an even number of ones in the input')

# Define the alphabet
moore.alphabet = {'0', '1'}

# Define the output alphabet
moore.stack_alphabet = {'even', 'odd'}

# Add states to the Moore machine
# Adding outputs that are not yet in the stack alphabet will add them to the stack alphabet
moore.add_state('S_even', output='even')
moore.add_state('S_odd', output='odd')

# Add transitions to the Moore machine
moore.add_transition('S_even', 'S_even', '0')
moore.add_transition('S_even', 'S_odd', '1')
moore.add_transition('S_odd', 'S_odd', '0')
moore.add_transition('S_odd', 'S_even', '1')

# Set the initial state of the Moore machine
moore.set_initial_state('S_even')

# Define input
input_string = '1010101'

# Process input
result = moore.process_input(input_string)

print(result)
