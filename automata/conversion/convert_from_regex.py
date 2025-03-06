from automata.automaton import Automaton
from automata.transition import Transition
from typing import Dict, Optional, Set


class AutomatonToRegexConverter:
    def __init__(self, automaton: Automaton):
        self.automaton = automaton
        self.transition_regex: Dict[str, Dict[str, str]] = {}  # Regex between states

    def initialize_regex_transitions(self):
        """Set up initial regex table from automaton transitions."""
        # Initialize an empty regex for each state pair
        for state_name in self.automaton.states:
            self.transition_regex[state_name] = {
                target_name: "" for target_name in self.automaton.states
            }

        # Populate initial regex from transitions
        for state_name, state in self.automaton.states.items():
            for symbol, transitions in state.transitions.items():
                if isinstance(transitions, list):  # For NFA
                    for transition in transitions:
                        self._add_transition(state_name, transition.target.name, symbol)
                else:  # For DFA
                    self._add_transition(state_name, transitions.target.name, symbol)

    def _add_transition(self, source: str, target: str, symbol: str):
        """Add a transition with regex."""
        current_regex = self.transition_regex[source][target]
        new_regex = symbol if not current_regex else f"{current_regex}|{symbol}"
        self.transition_regex[source][target] = new_regex

    def eliminate_state(self, state_name: str):
        """Eliminate a state by updating regex transitions."""
        state = self.automaton.states[state_name]
        loop_regex = self.transition_regex[state_name][state_name]  # R_xx (self-loop)

        # Update transitions for each pair (p, q) with paths passing through `state_name`
        for p in self.automaton.states:
            if p == state_name:
                continue
            for q in self.automaton.states:
                if q == state_name:
                    continue

                # R_pq = R_pq | (R_px R_xx* R_xq)
                new_path = ""
                if self.transition_regex[p][state_name] and self.transition_regex[state_name][q]:
                    path_px = self.transition_regex[p][state_name]
                    path_xq = self.transition_regex[state_name][q]
                    new_path = f"{path_px}({loop_regex})*{path_xq}" if loop_regex else f"{path_px}{path_xq}"

                # Combine existing paths
                if self.transition_regex[p][q]:
                    self.transition_regex[p][q] += f"|{new_path}" if new_path else ""
                else:
                    self.transition_regex[p][q] = new_path

        # Remove eliminated state’s transitions
        for p in self.transition_regex:
            self.transition_regex[p].pop(state_name, None)
        self.transition_regex.pop(state_name, None)

    def to_regex(self) -> Optional[str]:
        """Convert the entire automaton to a regex by state elimination."""
        self.initialize_regex_transitions()

        # Remove all non-initial and non-final states one by one
        non_final_states = {
            state_name for state_name, state in self.automaton.states.items() if not state.is_final
        }
        for state_name in list(non_final_states):
            if state_name != self.automaton.initial_state.name:
                self.eliminate_state(state_name)

        # Return the final regex between initial and final states
        initial = self.automaton.initial_state.name
        final_states = [name for name, state in self.automaton.states.items() if state.is_final]
        if final_states:
            regex = "|".join(self.transition_regex[initial][f] for f in final_states)
            return regex if regex else None
        return None
