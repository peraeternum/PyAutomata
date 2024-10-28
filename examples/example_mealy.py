from automata.automata_classes import MEALY

# Create a Mealy machine
mealy = MEALY('Even number of ones', 'Checks if there is an even number of ones in the input')

# Define the alphabet
mealy.alphabet = {'0', '1'}

#Define the output alphabet
mealy.stack_alphabet = {'even', 'odd'}

# Add states to the Mealy machine
mealy.add_state('S_even')
mealy.add_state('S_odd')

# Add transitions to the Mealy machine
# Adding outputs that are not yet in the stack alphabet will add them to the stack alphabet
mealy.add_transition('S_even', "S_even", "0", 'even')
mealy.add_transition('S_even', 'S_odd', '1', 'odd')
mealy.add_transition('S_odd', 'S_odd', '0', 'odd')
mealy.add_transition('S_odd', 'S_even', '1', 'even')

# Set the initial state of the Mealy machine
mealy.set_initial_state('S_even')

# Define input
input_string = '1010101'

# Process input
result = mealy.process_input(input_string)
print(result)

# Export to FLACI
