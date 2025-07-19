# PyAutomata: A Modern Library for Formal Automata

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/pyautomata.svg)](https://badge.fury.io/py/pyautomata) <!--- Placeholder for when you publish to PyPI -->
[![Build Status](https://travis-ci.org/your-username/pyautomata.svg?branch=main)](https://travis-ci.org/your-username/pyautomata) <!--- Placeholder for CI -->
[![Code Coverage](https://codecov.io/gh/your-username/pyautomata/branch/main/graph/badge.svg)](https://codecov.io/gh/your-username/pyautomata) <!--- Placeholder for Code Coverage -->

**PyAutomata** is a powerful and intuitive Python library for simulating, manipulating, and visualizing formal automata. Designed with a clean, object-oriented API, it's the perfect tool for students, educators, and researchers in the field of theoretical computer science and formal languages.

---

### Features

*   **Comprehensive Automata Support:**
    *   Deterministic Finite Automata (DFA)
    *   Non-deterministic Finite Automata (NFA), including ε-transitions
    *   Deterministic Pushdown Automata (DPDA)
    *   Non-deterministic Pushdown Automata (NPDA)
    *   Moore Machines
    *   Mealy Machines
    *   Standard Turing Machines
    *   Multi-Tape Turing Machines (coming soon)
*   **Powerful Utilities:**
    *   Convert any DFA/NFA to its equivalent regular expression using the state elimination method.
    *   Check automata for completeness and automatically add transitions to a trap state.
*   **Seamless Interoperability:**
    *   Export and import automata to and from the **FLACI** JSON format, allowing you to visualize and edit your machines in a graphical interface.
*   **Intuitive API:**
    *   A clean, consistent API across all automaton types.
    *   Advanced helpers like the `Push` class for defining complex PDA stack operations effortlessly.

### Installation

You can install PyAutomata directly from PyPI:

```bash
pip install pyautomata
```

### Quick Start

Let's create a simple DFA that accepts binary strings ending in '0' (i.e., even binary numbers).

```python
from automata.automata_classes import DFA

# 1. Create a new DFA
dfa = DFA(name="Even Binary Numbers", description="Accepts binary strings ending in '0'")

# 2. Add states
# The first state added is automatically the initial state.
dfa.add_state('q0', is_final=True)  # Accepts if we end here
dfa.add_state('q1')

# 3. Add transitions
dfa.add_transition('q0', 'q0', '0') # If in accepting state and we see a 0, stay
dfa.add_transition('q0', 'q1', '1') # If we see a 1, move to non-accepting
dfa.add_transition('q1', 'q0', '0') # If in non-accepting and we see a 0, become accepting
dfa.add_transition('q1', 'q1', '1') # If we see a 1, stay non-accepting

# 4. Process an input string
input_string = "10110"
is_accepted = dfa.process_input(input_string)

print(f"The string '{input_string}' is accepted: {is_accepted}")
# Output: The string '10110' is accepted: True

# Process another input string
input_string_2 = "1011"
is_accepted_2 = dfa.process_input(input_string_2)

print(f"The string '{input_string_2}' is accepted: {is_accepted_2}")
# Output: The string '1011' is accepted: False
```

### More Examples

#### NPDA for the language {aⁿbⁿ | n ≥ 0}

```python
from automata.automata_classes import NPDA

# NPDA for a^n b^n
npda = NPDA(name="a^n b^n")

# Add states
npda.add_state("q0", is_final=True) # Accepting empty string
npda.add_state("q1")
npda.add_state("q2", is_final=True)

npda.set_initial_state("q0")
npda.initial_stack = ['Z']

# Transitions
npda.add_transition("q0", "q1", "a", "Z", ["A", "Z"]) # Push A for first 'a'
npda.add_transition("q1", "q1", "a", "A", ["A", "A"]) # Push A for subsequent 'a's
npda.add_transition("q1", "q2", "b", "A", [])       # Pop A for first 'b'
npda.add_transition("q2", "q2", "b", "A", [])       # Pop A for subsequent 'b's

# Test the NPDA
print(f"aaabbb is accepted: {npda.process_input('aaabbb')}") # True
print(f"aabb is accepted: {npda.process_input('aabb')}")     # True
print(f"aaab is accepted: {npda.process_input('aaab')}")     # False
print(f"ε is accepted: {npda.process_input('')}")           # True
```

### Contributing

Contributions are welcome! Whether it's bug reports, feature requests, or pull requests, please feel free to get involved. Please read our `CONTRIBUTING.md` file for guidelines on how to contribute.

### License

This project is licensed under the MIT License - see the `LICENSE` file for details.