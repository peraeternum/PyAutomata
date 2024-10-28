from automata.automata_classes import DPDA
from automata.serialize.serialize_flaci import export_to_flaci

# Initialisiere den DPDA
dpda = DPDA("Palindrome_a_c_a", "Accepts strings of the form a^n c a^n")

# Zustände definieren
dpda.add_state("q0")  # Startzustand
dpda.add_state("q1")  # Zustand nach Lesen von c
dpda.add_state("q2")  # Zustand, um a's nach c zu lesen
dpda.add_state("q3", is_final=True)  # Endzustand

# Übergänge hinzufügen
dpda.add_transition("q0", "q0", "a", "|", ["A", "|"])  # Erster 'a', legt "A" auf den Stack
dpda.add_transition("q0", "q0", "a", "A", ["A", "A"])  # Weitere 'a', legt für jedes 'a' ein weiteres "A" auf den Stack
dpda.add_transition("q0", "q1", "c", "|", ["|"])       # Wechselt zu q1 beim Lesen von 'c'
dpda.add_transition("q1", "q1", "c", "|", ["|"])       # Verarbeitet mehrere 'c' (optional, hier nicht wirklich benötigt)
dpda.add_transition("q1", "q2", "a", "A", [])          # Erster 'a' nach c, entfernt ein "A" vom Stack
dpda.add_transition("q2", "q2", "a", "A", [])          # Weitere 'a', entfernt für jedes 'a' ein "A" vom Stack
dpda.add_transition("q2", "q3", "", "|", ["|"])        # Wenn Stack leer, wechselt in den Endzustand q3

# Teste den DPDA mit einigen Eingaben
input_strings = ["a", "aaacaa", "aaaacaaa", "abc", "aaabaaa", "aaaaa"]

for input_string in input_strings:
    result = dpda.process_input(input_string)
    print(f"Input '{input_string}' accepted? {result}")


export_to_flaci(dpda)