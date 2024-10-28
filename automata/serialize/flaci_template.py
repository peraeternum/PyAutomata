import json
from collections import defaultdict


def flaci_template(automaton):
    automaton_types_flaci = {
        "DFA": "DEA",
        "NFA": "NEA",
        "MEALY": "MEALY",
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
            "Transitions": transition_list(state, automaton.type),
            "Start": state == automaton.initial_state,
            "Output": state.output if hasattr(state, "output") else None
        }
        for state in automaton.states.values()
    ]

    automaton_dict = {
        "name": automaton.name,
        "description": automaton.description,
        "type": automaton_types_flaci.get(automaton.type),
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


def transition_list(state, machine_type):
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

        if machine_type == "MEALY":
            if transition.output not in transitions[key]["Labels"]:
                transitions[key]["Labels"].append([str(transition.symbol), str(transition.output)])
        elif machine_type in ["NPDA", "DPDA"]:
            transitions[key]["Labels"].append([str(transition.stack_symbol), str(transition.symbol), transition.stack_push])
        else:
            if transition.symbol not in transitions[key]["Labels"]:
                transitions[key]["Labels"].append(str(transition.symbol))

    return list(transitions.values())


def flaci_to_python_template(flaci_json):
    automaton_types = {
        "DEA": "DFA",
        "NEA": "NFA",
        "MEALY": "MEALY",
        "MOORE": "MOORE",
        "DKA": "DPDA",
        "NKA": "NPDA"
    }

    with open(flaci_json, 'r', encoding='utf-8-sig') as f:
        flaci = json.load(f)

    name = flaci["name"]
    description = flaci.get("description", "")
    automaton_type = flaci["type"]
    automaton = flaci["automaton"]

    alphabet = automaton["Alphabet"]
    stack_alphabet = automaton["StackAlphabet"]
    states = automaton["States"]
    allow_partial = automaton.get("allowPartial", False)

    class_name = automaton_type
    states_string = ""
    transition_string = ""

    for state in states:
        states_string += f'{class_name}.add_state("{state["Name"]}", "{(state["ID"])}", {state.get("Final", False)}, "{state.get("Output", "")}")\n'
        for transition in state["Transitions"]:
            if automaton_type in ["DKA", "NKA"]:
                for label in transition["Labels"]:
                    transition_string += (f'{class_name}.add_transition("{transition["Source"]}", "{transition["Target"]}", '
                                          f'"{label[1]}", "{label[0]}", {label[2]}, By.ID)\n')
            else:
                transition_string += (f'{class_name}.add_transition("{transition["Source"]}", "{transition["Target"]}", '
                                      f'{transition["Labels"]}, "{transition.get("Output", "")}", {transition["x"]}, '
                                      f'{transition["y"]}, By.ID)\n')

    if automaton_type == "NEA":
        import_type = "from automata.nfa import NFA"
    else:
        import_type = f"from automata.automata_classes import {automaton_types.get(automaton_type, automaton_type)}"

    return (
        f"""{import_type}
from automata.state import By\n

{class_name} = {automaton_types.get(automaton_type)}("{name}", "{description}", {allow_partial})\n

{class_name}.alphabet = {set(alphabet)}\n
{class_name}.stack_alphabet = {set(stack_alphabet)}\n

{states_string}

{transition_string}
"""
    )