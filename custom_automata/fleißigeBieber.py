import itertools
import time
import math
from os import getenv
from multiprocessing import Pool, cpu_count
from functools import partial
from typing import List, Tuple, Iterator
import gc

# Import the Turing class (assuming it's in the same directory or properly imported)
from automata.automata_classes import Turing


def calculate_total_combinations(states: int, symbols: int) -> int:
    """Calculate total number of possible combinations."""
    transitions_per_pair = (states + 1) * symbols * 2  # +1 for halt state, *2 for L/R moves
    return transitions_per_pair ** (states * symbols)


def create_turing_machine(combination: tuple, states: int, symbols: int, symbols_list: list) -> Tuple[bool, Turing]:
    """Create a single Turing machine from a combination of transitions."""
    TM = Turing(blank_symbol="0")

    for state in range(1, states + 1):
        TM.add_state(str(state))
    TM.add_state("H", is_final=True)

    for i, (next_state, write_symbol, move) in enumerate(combination):
        current_state = str((i // symbols) + 1)
        read_symbol = symbols_list[i % symbols]

        if current_state == "H":
            return False, None

        TM.add_transition(current_state, next_state, read_symbol, write_symbol, move)

    return True, TM


def generator_machine_combinations(states: int, symbols: int):
    """
    Generate machine combinations as a memory-efficient generator.

    Args:
        states (int): Number of states
        symbols (int): Number of symbols

    Yields:
        tuple: A combination of transitions
    """
    symbols_list = [str(i) for i in range(symbols)]
    moves = ["L", "R"]
    next_states = [str(i) for i in range(1, states + 1)] + ["H"]

    transitions = list(itertools.product(next_states, symbols_list, moves))
    num_pairs = states * symbols

    # Use a generator instead of storing all combinations in memory
    for combination in itertools.product(transitions, repeat=num_pairs):
        yield combination


def process_combination_chunk(chunk: List[tuple], states: int, symbols: int, symbols_list: list) -> List[Turing]:
    """
    Process a chunk of machine combinations and return valid Turing machines.

    Args:
        chunk (List[tuple]): A chunk of machine combinations
        states (int): Number of states
        symbols (int): Number of symbols
        symbols_list (List[str]): List of symbol representations

    Returns:
        List[Turing]: List of valid Turing machines
    """
    valid_machines = []
    for combination in chunk:
        valid, tm = create_turing_machine(combination, states, symbols, symbols_list)
        if valid:
            valid_machines.append(tm)
    return valid_machines


def bb(states: int, symbols: int, chunk_size: int = 1000):
    """
    Generate all possible Turing machines with memory-efficient approach.

    Args:
        states (int): Number of states
        symbols (int): Number of symbols
        chunk_size (int): Number of combinations to process in each chunk

    Returns:
        List[Turing]: List of valid Turing machines
    """
    total_combinations = calculate_total_combinations(states, symbols)
    print(f"\nTotal possible combinations: {total_combinations:,}")

    symbols_list = [str(i) for i in range(symbols)]
    num_processes = max(1, cpu_count() - 1)  # Leave one core free
    print(f"Using {num_processes} CPU cores")

    # Track generation progress
    processed_combinations = 0
    last_print_time = time.time()
    start_time = time.time()

    # Generator for machine combinations
    combinations = generator_machine_combinations(states, symbols)

    # Temporary storage for machines
    turing_machines = []

    with Pool(processes=num_processes) as pool:
        while True:
            # Create a chunk of combinations
            chunk = list(itertools.islice(combinations, chunk_size))

            if not chunk:
                break

            # Process chunk in parallel
            chunk_machines = pool.apply(
                process_combination_chunk,
                args=(chunk, states, symbols, symbols_list)
            )

            # Extend machines list
            turing_machines.extend(chunk_machines)
            processed_combinations += len(chunk)

            # Progress tracking
            current_time = time.time()
            if current_time - last_print_time >= 1.0:
                percentage = (processed_combinations / total_combinations) * 100
                print(
                    f"Generating machines: {percentage:.2f}% complete ({processed_combinations:,}/{total_combinations:,})"
                )
                last_print_time = current_time

            # Periodic garbage collection
            if processed_combinations % 10000 == 0:
                gc.collect()

    print(f"\nGenerated {len(turing_machines):,} valid Turing machines")
    return turing_machines


def evaluate_machine(args: tuple) -> Tuple[int, list]:
    """
    Evaluate a single Turing machine and return the number of 1s and tape.

    Args:
        args (tuple): (Turing machine, input length)

    Returns:
        Tuple[int, list]: Number of 1s and final tape state
    """
    tm, input_length = args
    try:
        result, tape = tm.process_input("0" * input_length)
        if result:
            return tape.count("1"), tape
        return 0, []
    except Exception:
        return 0, []


def parallel_evaluate_machines(machines: List[Turing], input_length: int = 10) -> Tuple[int, list]:
    """
    Evaluate machines in parallel to find the best result.

    Args:
        machines (List[Turing]): List of Turing machines to evaluate
        input_length (int): Length of initial input tape

    Returns:
        Tuple[int, list]: Best number of 1s and corresponding tape
    """
    total_machines = len(machines)
    processed_machines = 0
    last_print_time = time.time()

    with Pool(processes=max(1, cpu_count() - 1)) as pool:
        # Create evaluation arguments
        eval_args = [(tm, input_length) for tm in machines]

        most_ones = 0
        best_tape = []

        # Process evaluations and track progress
        for ones, tape in pool.imap_unordered(evaluate_machine, eval_args):
            processed_machines += 1
            if ones > most_ones:
                most_ones = ones
                best_tape = tape

            current_time = time.time()
            if current_time - last_print_time >= 1.0:
                percentage = (processed_machines / total_machines) * 100
                print(f"Evaluating machines: {percentage:.2f}% complete ({processed_machines:,}/{total_machines:,})")
                last_print_time = current_time

    return most_ones, best_tape


def main():
    states = 3
    symbols = 2

    print(f"Starting Busy Beaver search for {states} states and {symbols} symbols")

    # Machine Generation
    start = time.time()
    tms = bb(states, symbols)
    generation_time = time.time() - start
    print(f"\nGeneration time: {generation_time:.2f} seconds")

    # Machine Evaluation
    start = time.time()
    most_ones, best_tape = parallel_evaluate_machines(tms)
    evaluation_time = time.time() - start

    print(f"\nEvaluation time: {evaluation_time:.2f} seconds")
    print(f"Best result: {best_tape}")
    print(f"Number of 1s: {most_ones}")
    print(f"\nTotal time: {generation_time + evaluation_time:.2f} seconds")
    print("Done!")


if __name__ == "__main__":
    main()