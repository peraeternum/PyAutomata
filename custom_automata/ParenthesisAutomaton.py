from automata.automata_classes import DPDA
from automata.state import By


DKA = DPDA("KlammerKeller", "", False)


DKA.alphabet = {')', '('}

DKA.stack_alphabet = {'#', '('}


DKA.add_state("q0", "1", False, "")
DKA.add_state("q2", "3", True, "")


DKA.add_transition("1", "1", "(", "#", ['(', '#'], By.ID)
DKA.add_transition("1", "1", "(", "(", ['(', '('], By.ID)
DKA.add_transition("1", "3", ")", "#", [], By.ID)
DKA.add_transition("1", "3", ")", "(", [], By.ID)
DKA.add_transition("3", "1", "(", "#", ['(', '#'], By.ID)
DKA.add_transition("3", "1", "(", "(", ['(', '('], By.ID)
DKA.add_transition("3", "3", ")", "(", [], By.ID)

