def json_template(automaton):
    automaton_dict = {
        'name': automaton.name,
        'description': automaton.description,
        'type': automaton.type,
        'automaton': {

        }
    }