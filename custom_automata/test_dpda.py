from automata.automata_classes import DPDA

dpda = DPDA()

dpda.initial_stack = ["a"]

dpda.add_state("q0")
dpda.add_state("q1")


print(dpda.process_input("a"))
