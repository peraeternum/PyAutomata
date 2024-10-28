from automata.automata_classes import NPDA

npda = NPDA()

# Add states
npda.add_state("q0")
npda.add_state("q1")
npda.add_state("q2", is_final=True)

npda.initial_stack = ['X']

# Add transitions for a^n b^n
npda.add_transition("q0", "q1", "a", "X", ["X"])  # Push X for first 'a'
npda.add_transition("q1", "q2", "", "", [])    # Pop X for subsequent 'a's
npda.add_transition("q1", "q1", "a", "", ["X"])  # Push X for subsequent 'a's
npda.add_transition("q1", "q2", "b", "X", [])    # Pop X for first 'b'
npda.add_transition("q2", "q2", "b", "X", [])    # Pop X for subsequent 'b's
npda.add_transition("q0", "q2", "", "", [])      # Epsilon transition for empty string

# Test
print(npda.process_input("aabb"))  # Should print processing message and return True