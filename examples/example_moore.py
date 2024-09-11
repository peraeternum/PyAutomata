from automata.automata_classes import MOORE

# Create a Moore machine
moore = MOORE('Even number of ones', 'Checks if there is an even number of ones in the input')

# Add states to the Moore machine
moore.add_state('S_even', output='0')
moore.add_state('S_odd', output='1')

# Add transitions to the Moore machine
moore.add_transition('S_even', '0', 'S_even')
moore.add_transition('S_even', '1', 'S_odd')
moore.add_transition('S_odd', '0', 'S_odd')
moore.add_transition('S_odd', '1', 'S_even')

# Set the initial state of the Moore machine
moore.set_initial_state('S_even')

# Define input
input_string = '1010101'

# Process input
result = moore.process_input(input_string)

print(result)