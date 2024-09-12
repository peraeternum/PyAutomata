import json

from automata.serialize.flaci_template import flaci_template, flaci_to_python_template


def export_to_flaci(automaton):
    automaton_name = automaton.name if automaton.name else automaton.type
    with open(f"{automaton_name}.json", "w") as f:
        f.write(json.dumps(flaci_template(automaton), indent=4))


def flaci_to_python(flaci_json):
    with open('flaci_automaton.py', 'w', encoding='utf-8') as f:
        f.write(flaci_to_python_template(flaci_json))


flaci_to_python(r"C:\Users\benne\Downloads\Automaton_240808MooreParkscheinautomatLasse2.json")