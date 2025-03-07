from pprint import pprint

from automata.automata_classes import Turing

base_two = 2
base_two_values = [i for i in range(base_two)]

TM = Turing("BaseAddition", "", "|")

def create_states(base, values):
    end = "*"
    blank = TM.blank_symbol
    TM.add_state("xy0") # Base state, x and y will be read in and carry is 0
    TM.add_state("xy1")
    TM.add_state("+0") # Seperator between numbers
    TM.add_state("+1") # Seperator between numbers with carry

    # Add all necessary x, y and carry states
    for i in range(base):
        for k in range(2):
            TM.add_state(f"{k}{end}{i}")  # End of the second number
            TM.add_state(f"{i}y{k}")
        for j in range(base):
            for k in range(2):
                state_name = f"{i}{j}{k}"
                if ((i == 0 and k == 1) or
                    (i == 0 and j != 0 and k == 0) or
                    (i != 0 and j == 0 and k == 1)):
                    continue
                if state_name not in TM.states:
                    TM.add_state(state_name)
                    loop_values = values+[end]
                    TM.loop_left(state_name, loop_values)

                    total = i + j + k
                    write_digit = total % base
                    new_carry = total // base
                    write_state = f"w{write_digit}{new_carry}"

                    # Add the writing state which writes the new digit and remembers the new carry
                    TM.add_state(write_state)
                    TM.loop_left(write_state, values)
                    TM.add_transition(write_state, f"xy{new_carry}", blank, write_digit, "R")

                    TM.add_transition(state_name, write_state, blank, blank, "L")

    # Go right for all "|", and all values until "+" is read and stay in "xy0"
    start_loop_values = [blank] + values
    TM.loop_right("xy0", start_loop_values)
    # When + is met, go left and move to state "+"
    TM.add_transition("xy0", "+0", "+", "+", "L")

    TM.loop_right("xy1", start_loop_values)
    TM.add_transition("xy1", "+1", "+", "+", "L")

    # Scan the last digit of the first number and go in the correct state
    for i in range(base):
        # Replace a digit with "+", to mark it as read
        TM.add_transition("+0", f"{i}y0", values[i], '+', "R")
        TM.add_transition("+1", f"{i}y1", values[i], '+', "R")

        TM.loop_right(f"{i}y0", values+["+"])
        TM.add_transition(f"{i}y0", f"0{end}{i}", end, end, "L")

        TM.loop_right(f"{i}y1", values+["+"])
        TM.add_transition(f"{i}y1", f"1{end}{i}", end, end, "L")

        # If there is no last digit in the second number, go into the state {i}00 or some other state
        for k in range(2):
            if f"{i}{k}0" in TM.states:
                TM.add_transition(f"{k}{end}{i}", f"{i}{k}0", "+", "+", "L")
            elif  f"{k}{i}0" in TM.states:
                TM.add_transition(f"{k}{end}{i}", f"{k}{i}0", "+", "+", "L")

        # Scan the last digit of the second number and transition to the correct state
        for j in range(base):
            for bit in ("0", "1"):  # Handle both '0' and '1' cases
                current_state = f"{bit}{end}{i}"
                possible_states = [
                    f"{i}{j}{bit}",
                    f"{j}{i}{bit}",
                    f"{i}{bit}{j}",
                    f"{bit}{i}{j}",
                    f"{j}{bit}{i}"
                ]

                for state in possible_states:
                    if state in TM.states:
                        TM.add_transition(current_state, state, values[j], end, "L")
                        break  # Ensure only the first matching state is used

create_states(base_two, base_two_values)

print_states = False
print_transitions = False
print_detailed_transitions = True

if print_states:
    pprint(TM.states)

if print_transitions:
    for state in TM.states.values():
        print(state.name)
        pprint(state.transitions)
        print()

if print_detailed_transitions:
    total_transitions = 0
    for state in TM.states.values():
        total_transitions += len(state.transitions)
        for transition in state.transitions.values():
            print(state.name, transition.target.name, transition.tape_symbol, transition.tape_write, transition.move)
    print(total_transitions)
print(len(TM.states))