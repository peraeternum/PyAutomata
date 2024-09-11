from collections import defaultdict

def flaci_template(automaton):

    automaton_types = {
        "DFA": "DEA",
        "NFA": "NEA",
        "MEAlY": "MEAlY",
        "MOORE": "MOORE",
        "DPDA": "DKA",
        "NPDA": "NKA"
    }

    automaton_states = [
        {
            "ID": state.id,
            "Name": state.name,
            "x": state.x,
            "y": state.y,
            "Final": state.is_final,
            "Radius": state.radius,
            "Transitions": transition_list(state),
            "Start": state == automaton.initial_state,
            "Output": state.output if hasattr(state, "output") else None
        }
        for state in automaton.states.values()
    ]

    automaton_dict = {
        "name": automaton.name,
        "description": automaton.description,
        "type": automaton_types.get(automaton.type),
        "automaton": {
            "acceptCache": [],
            "simulationInput": automaton.inputs[0] if automaton.inputs else [],
            "Alphabet": list(automaton.alphabet),
            "StackAlphabet": list(automaton.stack_alphabet),
            "States": automaton_states,
            "lastInputs": [],
            "allowPartial": automaton.allow_partial
        }
    }

    return automaton_dict

def transition_list(state):
    transitions = defaultdict(lambda: {
        "Source": None, "Target": None, "x": None, "y": None, "Labels": []
    })
    for transition in state.transitions.values():
        key = transition.target.name
        if transitions[key]["Source"] is None:
            transitions[key]["Source"] = transition.source.id
            transitions[key]["Target"] = transition.target.id
            transitions[key]["x"] = transition.x
            transitions[key]["y"] = transition.y

        if transition.symbol not in transitions[key]["Labels"]:
            transitions[key]["Labels"].append(str(transition.symbol))

    print(transitions)
    return list(transitions.values())

