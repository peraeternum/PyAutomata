import json

from automata.serialize.flaci_template import flaci_template


def export_to_flaci(automaton):
    automaton_name = automaton.name if automaton.name else automaton.type
    with open(f"{automaton_name}.json", "w") as f:
        f.write(json.dumps(flaci_template(automaton), indent=4))


