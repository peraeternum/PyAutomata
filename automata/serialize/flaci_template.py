import json
from collections import defaultdict


def flaci_template(automaton):
    automaton_types_flaci = {
        "DFA": "DEA",
        "NFA": "NEA",
        "MEALY": "MEALY",
        "MOORE": "MOORE",
        "DPDA": "DKA",
        "NPDA": "NKA",
        "Turing": "TM"
    }

    automaton_states = [
        {
            "ID": int(state.id),
            "Name": state.name,
            "x": state.x,
            "y": state.y,
            "Final": state.is_final,
            "Radius": state.radius,
            "Transitions": transition_list(state, automaton.type),
            "Start": state == automaton.initial_state,
            **({"Output": state.output} if automaton.type == "MOORE" and hasattr(state, "output") else {})
        }
        for state in automaton.states.values()
    ]

    if automaton.type == "Turing":
        stack_alphabet = [automaton.blank_symbol] + sorted(set(automaton.stack_alphabet) - {automaton.blank_symbol})
    elif automaton.type in ["NPDA", "DPDA"]:
        stack_alphabet = [automaton.initial_stack[0]] + sorted(set(automaton.stack_alphabet) -
            {automaton.initial_stack[0]})
    else: stack_alphabet = list(automaton.stack_alphabet)

    print(stack_alphabet)

    automaton_dict = {
        "name": automaton.name,
        "description": automaton.description,
        "type": automaton_types_flaci.get(automaton.type),
        "automaton": {
            "acceptCache": [],
            "simulationInput": automaton.inputs[0] if automaton.inputs else [],
            "Alphabet": list(automaton.alphabet),
            "StackAlphabet": stack_alphabet,
            "States": automaton_states,
            "lastInputs": [],
        }
    }

    if automaton.type not in ["NPDA", "DPDA", "Turing", "NFA"]:
        automaton_dict["allowPartial"] = automaton.allow_partial
    return automaton_dict


def transition_list(state, machine_type):
    transitions = defaultdict(lambda: {
        "Source": -1, "Target": -1, "x": None, "y": None, "Labels": []
    })

    for symbol, trans_list in state.transitions.items():
        # Handle case where transitions is a list
        if isinstance(trans_list, list):
            for transition in trans_list:
                key = transition.target.name
                if transitions[key]["Source"] == -1:
                    transitions[key]["Source"] = int(transition.source.id)
                    transitions[key]["Target"] = int(transition.target.id)
                    transitions[key]["x"] = getattr(transition, 'x', None)
                    transitions[key]["y"] = getattr(transition, 'y', None)

                if machine_type == "MEALY":
                    if transition.output not in transitions[key]["Labels"]:
                        transitions[key]["Labels"].append([str(symbol), str(transition.output)])
                elif machine_type in ["NPDA", "DPDA"]:
                    label = [str(transition.stack_symbol), str(symbol), transition.stack_push]
                    if label not in transitions[key]["Labels"]:
                        transitions[key]["Labels"].append(label)
                elif machine_type == "Turing":
                    label = [str(transition.tape_symbol), str(transition.tape_write), transition.move]
                    if symbol not in transitions[key]["Labels"]:
                        transitions[key]["Labels"].append(label)
                else:
                    if symbol not in transitions[key]["Labels"]:
                        transitions[key]["Labels"].append(str(symbol))
        else:
            # Handle single transition case
            transition = trans_list
            key = transition.target.name
            if transitions[key]["Source"] == -1:
                transitions[key]["Source"] = int(transition.source.id)
                transitions[key]["Target"] = int(transition.target.id)
                transitions[key]["x"] = getattr(transition, 'x', None)
                transitions[key]["y"] = getattr(transition, 'y', None)

            if machine_type == "MEALY":
                if transition.output not in transitions[key]["Labels"]:
                    transitions[key]["Labels"].append([str(symbol), str(transition.output)])
            elif machine_type in ["NPDA", "DPDA"]:
                label = [str(transition.stack_symbol), str(symbol), transition.stack_push]
                if label not in transitions[key]["Labels"]:
                    transitions[key]["Labels"].append(label)
            elif machine_type == "Turing":
                label = [str(transition.tape_symbol), str(transition.tape_write), transition.move]
                if symbol not in transitions[key]["Labels"]:
                    transitions[key]["Labels"].append(label)
            else:
                if symbol not in transitions[key]["Labels"]:
                    transitions[key]["Labels"].append(str(symbol))

    return list(transitions.values())


def flaci_to_python_template(flaci_json):
    automaton_types = {
        "DEA": "DFA",
        "NEA": "NFA",
        "MEALY": "MEALY",
        "MOORE": "MOORE",
        "DKA": "DPDA",
        "NKA": "NPDA",
        "TM": "Turing"
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

            elif automaton_type == "TM":
                for label in transition["Labels"]:
                    transition_string += (f'{class_name}.add_transition("{transition["Source"]}", "{transition["Target"]}", '
                                          f'"{label[0]}", "{label[1]}", "{label[2]}", By.ID)\n')

            else:
                transition_string += (f'{class_name}.add_transition("{transition["Source"]}", "{transition["Target"]}", '
                                      f'{transition["Labels"]}, "{transition.get("Output", "")}", {transition["x"]}, '
                                      f'{transition["y"]}, By.ID)\n')

    if automaton_type == "NEA":
        import_type = "from automata.nfa import NFA"
    elif automaton_type == "TM":
        import_type = "from automata.automata_classes import Turing"
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