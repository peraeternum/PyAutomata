from automata.automata_classes import Turing
from automata.transition import MappingType

TM = Turing()

operators = ['+', '-', '*', '/']
numbers = ['0', '1']

TM.alphabet = {'0', '1', '-', '+', '/', '*'}
TM.stack_alphabet = {'0', '1', '-', '+', '/', '*', '|', 'X', '(', ')', '$', 'S'}
"""
Meaning of the symbols:
0, 1: Binary numbers
-: Subtraction
+: Addition
*: Multiplication
/: Division
|: Separator
X: Marking used numbers
$: Marking used operators
S: Seperator between numbers in the output
"""

TM.add_state('parse_right')
TM.add_state('parse_left')
TM.add_state('find_operator') # Number on left added to output, we need to find and add operator
TM.add_state('find_number') # Operator found on the right of a number, we need to add number
TM.add_state('add_number') # Number addition starting now
TM.add_state('0')
TM.add_state('1')
TM.add_state('Output_0')
TM.add_state('Output_1')
TM.add_state('Add_S')
TM.add_state('+')
TM.add_state('-')
TM.add_state('*')
TM.add_state('/')
TM.add_state('+_stack')
TM.add_state('-_stack')
TM.add_state('*_stack')
TM.add_state('/_stack')
TM.add_state('+_output')
TM.add_state('-_output')
TM.add_state('*_output')
TM.add_state('/_output')
TM.add_state('add_*')
TM.add_state('add_/')
TM.add_state('add_+')
TM.add_state('add_-')
TM.add_state('check_stack')
TM.add_state('cs_output') # check_stack should be reached, moving through the output section
TM.add_state('cs_input') # check_stack should be reached, moving through the input section
TM.add_state('stack_end')
TM.add_state('+_end')
TM.add_state('-_end')
TM.add_state('*_end')
TM.add_state('/_end')
TM.add_state('pop_all')
TM.add_state('pop_multiplicative')

# Move to the right until we find an operator
TM.add_transition('parse_right', 'parse_right', numbers, numbers, 'R')
TM.add_transition('parse_right', 'parse_right', 'X', 'X', 'R')
TM.add_transition('parse_right', 'parse_right', 'S', 'S', 'R')
TM.add_transition('parse_right', 'parse_right', '|', '|', 'R')
TM.add_transition('parse_right', 'parse_right', '$', '$', 'R')

# If we find an operator, we start adding the number starting from the right
TM.add_transition('parse_right', 'find_number', operators, operators, 'L')

# Remember the number we found by going to it's corresponding state and mark it with X
TM.add_transition('find_number', '0', '0', 'X', 'L')
TM.add_transition('find_number', '1', '1', 'X', 'L')

# If after going left from an operator we find an X we need to go left until we find a number
TM.add_transition('find_number', 'find_number', 'X', 'X', 'L')

# If we find a '|' or a '$' we add a 'S' to the left of the last number in the output
# because we know we are done with the number
TM.add_transition('find_number', 'Add_S', '|', '|', 'L')
# Iterate to the complete left of the output to find the last number
TM.add_transition('Add_S', 'Add_S', numbers, numbers, 'L')
TM.add_transition('Add_S', 'find_operator', '|', 'S', 'R')

# After adding the S we go to the right until we find the operator
TM.add_transition('find_operator', 'find_operator', numbers, numbers, 'R')
TM.add_transition('find_operator', 'find_operator', 'S', 'S', 'R')
TM.add_transition('find_operator', 'find_operator', 'X', 'X', 'R')
TM.add_transition('find_operator', 'find_operator', '$', '$', 'R')
TM.add_transition('find_operator', 'find_operator', '|', '|', 'R')

# Move to the left until we find the blank symbol
TM.add_transition('0', '0', numbers, numbers, 'L')
TM.add_transition('0', '0', '$', '$', 'L')
TM.add_transition('1', '1', 'X', 'X', 'L')
TM.add_transition('1', '1', numbers, numbers, 'L')
TM.add_transition('1', '1', '$', '$', 'L')

# If we find a blank symbol we go into the output state which remembers the number
TM.add_transition('0', 'Output_0', '|', '|', 'L')
TM.add_transition('1', 'Output_1', '|', '|', 'L')

# Once in the output state we move to the left until we find the end of the last number
TM.add_transition('Output_0', 'Output_0', numbers, numbers, 'L')
TM.add_transition('Output_0', 'Output_0', 'S', 'S', 'L')
TM.add_transition('Output_1', 'Output_1', numbers, numbers, 'L')
TM.add_transition('Output_1', 'Output_1', 'S', 'S', 'L')

# After adding the number go to parse_right to find the next operator and add the next number
TM.add_transition('Output_0', 'parse_right', '|', '0', 'R')
TM.add_transition('Output_1', 'parse_right', '|', '1', 'R')

# After adding a number and finding the operator we add the operator to the operator stack on the right
TM.add_transition('find_operator', '+', '+', '$', 'R')
TM.add_transition('find_operator', '-', '-', '$', 'R')
TM.add_transition('find_operator', '*', '*', '$', 'R')
TM.add_transition('find_operator', '/', '/', '$', 'R')

# When in operator state we move to the right until we find the blank symbol
TM.add_transition('+', '+', numbers, numbers, 'R')
TM.add_transition('-', '-', numbers, numbers, 'R')
TM.add_transition('*', '*', numbers, numbers, 'R')
TM.add_transition('/', '/', numbers, numbers, 'R')

# Once we find the blank symbol we go to the end of the stack and find the last operator
# Now we compare it to any operator we find or add it if there is none
# If the operator is of higher precedence we pop it and add the new operator
# The popped operator is added to the output
# If the operator is of lower precedence we add it to the stack

TM.add_transition('+', '+_stack', '|', '|', 'R')
TM.add_transition('-', '-_stack', '|', '|', 'R')
TM.add_transition('*', '*_stack', '|', '|', 'R')
TM.add_transition('/', '/_stack', '|', '|', 'R')

# Go to the end now in the _stack states
TM.add_transition('+_stack', '+_stack', operators, operators, 'R')
TM.add_transition('-_stack', '-_stack', operators, operators, 'R')
TM.add_transition('*_stack', '*_stack', operators, operators, 'R')
TM.add_transition('/_stack', '/_stack', operators, operators, 'R')

# Don't forget to move through brackets
TM.add_transition('+_stack', '+_stack', '(', '(', 'R')
TM.add_transition('-_stack', '-_stack', '(', '(', 'R')
TM.add_transition('*_stack', '*_stack', '(', '(', 'R')
TM.add_transition('/_stack', '/_stack', '(', '(', 'R')

# If we find a blank symbol we go to the end of the stack
TM.add_transition('+_stack', '+_end', '|', '|', 'L')
TM.add_transition('-_stack', '-_end', '|', '|', 'L')
TM.add_transition('*_stack', '*_end', '|', '|', 'L')
TM.add_transition('/_stack', '/_end', '|', '|', 'L')

# Now compare last operator with the new operator
# If + or - is found we pop all operators of higher and equal precedence
TM.add_transition('+_end', '*_output', '*', '+', 'L')
TM.add_transition('+_end', '/_output', '/', '+', 'L')
TM.add_transition('+_end', '+_output', '+', '+', 'L')
TM.add_transition('+_end', '-_output', '-', '+', 'L')

TM.add_transition('-_end', '*_output', '*', '-', 'L')
TM.add_transition('-_end', '/_output', '/', '-', 'L')
TM.add_transition('-_end', '+_output', '+', '-', 'L')
TM.add_transition('-_end', '-_output', '-', '-', 'L')

# If * or / is found we pop all operators of equal precedence
TM.add_transition('*_end', '*_output', '*', '*', 'L')
TM.add_transition('*_end', '/_output', '/', '*', 'L')

TM.add_transition('/_end', '*_output', '*', '/', 'L')
TM.add_transition('/_end', '/_output', '/', '/', 'L')

# Or if + or - is found when we want to add * or / we just add * or / without popping anything
TM.add_transition('*_end', '*_end', '+', '+', 'R')
TM.add_transition('*_end', '*_end', '-', '-', 'R')
TM.add_transition('*_end', 'parse_left', '|', '*', 'L')

TM.add_transition('/_end', '/_end', '+', '+', 'R')
TM.add_transition('/_end', '/_end', '-', '-', 'R')
TM.add_transition('/_end', 'parse_left', '|', '/', 'L')

# Go left until we find output section
TM.add_transition('*_output', '*_output', '+', '+', 'L')
TM.add_transition('*_output', '*_output', '-', '-', 'L')
TM.add_transition('*_output', '*_output', '*', '*', 'L')
TM.add_transition('*_output', '*_output', '/', '/', 'L')
TM.add_transition('*_output', '*_output', numbers, numbers, 'L')
TM.add_transition('*_output', '*_output', 'X', 'X', 'L')
TM.add_transition('*_output', '*_output', '$', '$', 'L')
TM.add_transition('*_output', 'add_*', '|', '|', 'L')

# Go to the left of the end of the output section and add * to the output
TM.add_transition('add_*', 'add_*', '+', '+', 'L')
TM.add_transition('add_*', 'add_*', '-', '-', 'L')
TM.add_transition('add_*', 'add_*', '*', '*', 'L')
TM.add_transition('add_*', 'add_*', '/', '/', 'L')
TM.add_transition('add_*', 'add_*', numbers, numbers, 'L')
TM.add_transition('add_*', 'add_*', 'S', 'S', 'L')
TM.add_transition('add_*', 'cs_output', '|', '*', 'R')

# Now do the same for /
# Go left until we find output section
TM.add_transition('/_output', '/_output', '+', '+', 'L')
TM.add_transition('/_output', '/_output', '-', '-', 'L')
TM.add_transition('/_output', '/_output', '*', '*', 'L')
TM.add_transition('/_output', '/_output', '/', '/', 'L')
TM.add_transition('/_output', '/_output', numbers, numbers, 'L')
TM.add_transition('/_output', '/_output', 'X', 'X', 'L')
TM.add_transition('/_output', '/_output', '$', '$', 'L')
TM.add_transition('/_output', 'add_/', '|', '|', 'L')

# Go to the left of the end of the output section
TM.add_transition('add_/', 'add_/', '+', '+', 'L')
TM.add_transition('add_/', 'add_/', '-', '-', 'L')
TM.add_transition('add_/', 'add_/', '*', '*', 'L')
TM.add_transition('add_/', 'add_/', '/', '/', 'L')
TM.add_transition('add_/', 'add_/', numbers, numbers, 'L')
TM.add_transition('add_/', 'add_/', 'S', 'S', 'L')
TM.add_transition('add_/', 'cs_output', '|', '/', 'R')


TM.add_transition('-_output', '-_output', '+', '+', 'L')
TM.add_transition('-_output', '-_output', '-', '-', 'L')
TM.add_transition('-_output', '-_output', '*', '*', 'L')
TM.add_transition('-_output', '-_output', '/', '/', 'L')
TM.add_transition('-_output', '-_output', numbers, numbers, 'L')
TM.add_transition('-_output', '-_output', 'X', 'X', 'L')
TM.add_transition('-_output', '-_output', '$', '$', 'L')
TM.add_transition('-_output', 'add_-', '|', '|', 'L')

# Go to the left of the end of the output section
TM.add_transition('add_-', 'add_-', '+', '+', 'L')
TM.add_transition('add_-', 'add_-', '-', '-', 'L')
TM.add_transition('add_-', 'add_-', '*', '*', 'L')
TM.add_transition('add_-', 'add_-', '/', '/', 'L')
TM.add_transition('add_-', 'add_-', numbers, numbers, 'L')
TM.add_transition('add_-', 'add_-', 'S', 'S', 'L')
TM.add_transition('add_-', 'cs_output', '|', '/', 'R')


TM.add_transition('+_output', '+_output', '+', '+', 'L')
TM.add_transition('+_output', '+_output', '-', '-', 'L')
TM.add_transition('+_output', '+_output', '*', '*', 'L')
TM.add_transition('+_output', '+_output', '/', '/', 'L')
TM.add_transition('+_output', '+_output', numbers, numbers, 'L')
TM.add_transition('+_output', '+_output', 'X', 'X', 'L')
TM.add_transition('+_output', '+_output', '$', '$', 'L')
TM.add_transition('+_output', 'add_+', '|', '|', 'L')

# Go to the left of the end of the output section
TM.add_transition('add_+', 'add_+', '+', '+', 'L')
TM.add_transition('add_+', 'add_+', '-', '-', 'L')
TM.add_transition('add_+', 'add_+', '*', '*', 'L')
TM.add_transition('add_+', 'add_+', '/', '/', 'L')
TM.add_transition('add_+', 'add_+', numbers, numbers, 'L')
TM.add_transition('add_+', 'add_+', 'S', 'S', 'L')
TM.add_transition('add_+', 'cs_output', '|', '/', 'R')

# In the check stack state we go to the end of the operator stack, check what the new operator was
# Then we look at the operators to the left of the new one and pop them if they are of higher or equal precedence
# If they are of lower precedence we continue with the next number
TM.add_transition('cs_output', 'cs_output', operators, operators, 'R')
TM.add_transition('cs_output', 'cs_output', numbers, numbers, 'R')
TM.add_transition('cs_output', 'cs_output', 'S', 'S', 'R')
TM.add_transition('cs_output', 'cs_input', '|', '|', 'R')

TM.add_transition('cs_input', 'cs_input', operators, operators, 'R')
TM.add_transition('cs_input', 'cs_input', numbers, numbers, 'R')
TM.add_transition('cs_input', 'cs_input', 'X', 'X', 'R')
TM.add_transition('cs_input', 'cs_input', '$', '$', 'R')
TM.add_transition('cs_input', 'check_stack', '|', '|', 'R')

# Once we find the check_stack state we go to the end of the operator stack
TM.add_transition('check_stack', 'check_stack', operators, operators, 'R')
TM.add_transition('check_stack', 'check_stack', '(', '(', 'R')
TM.add_transition('check_stack', 'stack_end', '|', '|', 'L')

# Once we found stack end if the operator is a + or - we continue popping until we find a ( or the stack is empty
# If we find a * or / we pop all multiplicative operators at the top of the stack until we find a ( or a + or -
TM.add_transition('stack_end', 'pop_all', '+', '+', 'L')
TM.add_transition('stack_end', 'pop_all', '-', '-', 'L')

TM.add_transition('stack_end', 'pop_multiplicative', '*', '*', 'L')
TM.add_transition('stack_end', 'pop_multiplicative', '/', '/', 'L')

# Once in the pop_all state we pop all operators until we find a ( or the stack is empty (besides the last operator)


total_states = len(TM.states)
total_transitions = 0
for state in TM.states.values():
    total_transitions += len(state.transitions)

print(f'Total states: {total_states}')
print(f'Total transitions: {total_transitions}')