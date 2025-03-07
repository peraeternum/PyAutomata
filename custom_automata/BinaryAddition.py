from automata.automata_classes import Turing
from automata.serialize.serialize_flaci import export_to_flaci
from automata.state import By


TM = Turing("TuringMachine", "", "|")


TM.alphabet = {'1', '0', '$', '*'}

TM.stack_alphabet = {'$', '|', '*', '1', '0'}


TM.add_state("xy0", "1", False, "") # Initial state, marker x, y and carry 0
TM.add_state("$", "2", False, "") # Found the end of the first number
TM.add_state("1y0", "3", False, "") # First symbol of first number is 1
TM.add_state("0y0", "4", False, "") # First symbol of first number is 0
TM.add_state("*1", "5", False, "") # Found the end of the second number
TM.add_state("*2", "6", False, "") # Found the end of the second number
TM.add_state("110", "7", False, "") 
TM.add_state("100", "8", False, "")
TM.add_state("q0", "9", False, "")
TM.add_state("xy1", "10", False, "")
TM.add_state("000", "11", False, "")
TM.add_state("q1", "12", False, "")
TM.add_state("q2", "13", False, "")
TM.add_state("$2", "14", False, "")
TM.add_state("0y1", "15", False, "")
TM.add_state("1y1", "16", False, "")
TM.add_state("*3", "17", False, "")
TM.add_state("*4", "19", False, "")
TM.add_state("111", "20", False, "")
TM.add_state("q3", "21", False, "")
TM.add_state("q4", "22", False, "")
TM.add_state("q5", "23", False, "")
TM.add_state("q6", "24", False, "")
TM.add_state("q7", "25", False, "")
TM.add_state("q8", "26", False, "")
TM.add_state("q9", "27", True, "")
TM.add_state("cleanLeft", "28", False, "")
TM.add_state("q10", "29", False, "")
TM.add_state("q11", "30", False, "")
TM.add_state("q12", "31", False, "")
TM.add_state("q13", "32", False, "")


TM.add_transition("1", "1", "1", "1", "R", By.ID)
TM.add_transition("1", "1", "0", "0", "R", By.ID)
TM.add_transition("1", "1", "|", "|", "R", By.ID)
TM.add_transition("1", "2", "$", "$", "L", By.ID)
TM.add_transition("2", "3", "1", "$", "R", By.ID)
TM.add_transition("2", "22", "*", "*", "R", By.ID)
TM.add_transition("2", "4", "0", "$", "R", By.ID)
TM.add_transition("2", "29", "|", "|", "R", By.ID)
TM.add_transition("3", "3", "$", "$", "R", By.ID)
TM.add_transition("3", "3", "1", "1", "R", By.ID)
TM.add_transition("3", "3", "0", "0", "R", By.ID)
TM.add_transition("3", "5", "*", "*", "L", By.ID)
TM.add_transition("4", "4", "1", "1", "R", By.ID)
TM.add_transition("4", "4", "$", "$", "R", By.ID)
TM.add_transition("4", "4", "0", "0", "R", By.ID)
TM.add_transition("4", "6", "*", "*", "L", By.ID)
TM.add_transition("5", "7", "1", "*", "L", By.ID)
TM.add_transition("5", "8", "0", "*", "L", By.ID)
TM.add_transition("5", "8", "$", "$", "L", By.ID)
TM.add_transition("6", "8", "1", "*", "L", By.ID)
TM.add_transition("6", "11", "0", "*", "L", By.ID)
TM.add_transition("6", "11", "$", "$", "L", By.ID)
TM.add_transition("7", "7", "1", "1", "L", By.ID)
TM.add_transition("7", "7", "*", "*", "L", By.ID)
TM.add_transition("7", "7", "$", "$", "L", By.ID)
TM.add_transition("7", "7", "0", "0", "L", By.ID)
TM.add_transition("7", "9", "|", "|", "L", By.ID)
TM.add_transition("8", "8", "1", "1", "L", By.ID)
TM.add_transition("8", "8", "0", "0", "L", By.ID)
TM.add_transition("8", "8", "$", "$", "L", By.ID)
TM.add_transition("8", "8", "*", "*", "L", By.ID)
TM.add_transition("8", "13", "|", "|", "L", By.ID)
TM.add_transition("9", "9", "1", "1", "L", By.ID)
TM.add_transition("9", "9", "0", "0", "L", By.ID)
TM.add_transition("9", "10", "|", "0", "R", By.ID)
TM.add_transition("10", "10", "1", "1", "R", By.ID)
TM.add_transition("10", "10", "0", "0", "R", By.ID)
TM.add_transition("10", "10", "|", "|", "R", By.ID)
TM.add_transition("10", "14", "$", "$", "L", By.ID)
TM.add_transition("11", "11", "1", "1", "L", By.ID)
TM.add_transition("11", "11", "0", "0", "L", By.ID)
TM.add_transition("11", "11", "$", "$", "L", By.ID)
TM.add_transition("11", "11", "*", "*", "L", By.ID)
TM.add_transition("11", "12", "|", "|", "L", By.ID)
TM.add_transition("12", "12", "1", "1", "L", By.ID)
TM.add_transition("12", "12", "0", "0", "L", By.ID)
TM.add_transition("12", "1", "|", "0", "R", By.ID)
TM.add_transition("13", "13", "1", "1", "L", By.ID)
TM.add_transition("13", "13", "0", "0", "L", By.ID)
TM.add_transition("13", "1", "|", "1", "R", By.ID)
TM.add_transition("14", "15", "0", "$", "R", By.ID)
TM.add_transition("14", "16", "1", "$", "R", By.ID)
TM.add_transition("14", "31", "|", "|", "R", By.ID)
TM.add_transition("15", "15", "1", "1", "R", By.ID)
TM.add_transition("15", "15", "0", "0", "R", By.ID)
TM.add_transition("15", "15", "$", "$", "R", By.ID)
TM.add_transition("15", "17", "*", "*", "L", By.ID)
TM.add_transition("16", "16", "1", "1", "R", By.ID)
TM.add_transition("16", "16", "0", "0", "R", By.ID)
TM.add_transition("16", "16", "$", "$", "R", By.ID)
TM.add_transition("16", "19", "*", "*", "L", By.ID)
TM.add_transition("17", "7", "1", "*", "L", By.ID)
TM.add_transition("17", "8", "0", "*", "L", By.ID)
TM.add_transition("17", "8", "$", "$", "L", By.ID)
TM.add_transition("19", "7", "0", "*", "L", By.ID)
TM.add_transition("19", "7", "$", "$", "L", By.ID)
TM.add_transition("19", "20", "1", "*", "L", By.ID)
TM.add_transition("20", "20", "1", "1", "L", By.ID)
TM.add_transition("20", "20", "0", "0", "L", By.ID)
TM.add_transition("20", "20", "$", "$", "L", By.ID)
TM.add_transition("20", "20", "*", "*", "L", By.ID)
TM.add_transition("20", "21", "|", "|", "L", By.ID)
TM.add_transition("21", "21", "1", "1", "L", By.ID)
TM.add_transition("21", "21", "0", "0", "L", By.ID)
TM.add_transition("21", "10", "|", "1", "R", By.ID)
TM.add_transition("22", "22", "*", "*", "R", By.ID)
TM.add_transition("22", "28", "|", "|", "L", By.ID)
TM.add_transition("23", "23", "$", "$", "L", By.ID)
TM.add_transition("23", "24", "|", "|", "L", By.ID)
TM.add_transition("24", "24", "1", "1", "L", By.ID)
TM.add_transition("24", "24", "0", "0", "L", By.ID)
TM.add_transition("24", "25", "|", "1", "L", By.ID)
TM.add_transition("25", "25", "1", "1", "R", By.ID)
TM.add_transition("25", "25", "0", "0", "R", By.ID)
TM.add_transition("25", "25", "|", "|", "R", By.ID)
TM.add_transition("25", "26", "$", "|", "R", By.ID)
TM.add_transition("26", "26", "$", "|", "R", By.ID)
TM.add_transition("26", "26", "*", "|", "R", By.ID)
TM.add_transition("26", "27", "|", "|", "N", By.ID)
TM.add_transition("28", "28", "*", "|", "L", By.ID)
TM.add_transition("28", "28", "$", "|", "L", By.ID)
TM.add_transition("28", "27", "|", "|", "N", By.ID)
TM.add_transition("29", "29", "$", "$", "R", By.ID)
TM.add_transition("29", "29", "0", "0", "R", By.ID)
TM.add_transition("29", "29", "1", "1", "R", By.ID)
TM.add_transition("29", "30", "*", "*", "L", By.ID)
TM.add_transition("30", "22", "$", "$", "R", By.ID)
TM.add_transition("30", "11", "0", "*", "L", By.ID)
TM.add_transition("30", "8", "1", "*", "L", By.ID)
TM.add_transition("31", "31", "1", "1", "R", By.ID)
TM.add_transition("31", "31", "0", "0", "R", By.ID)
TM.add_transition("31", "31", "$", "$", "R", By.ID)
TM.add_transition("31", "32", "*", "*", "L", By.ID)
TM.add_transition("32", "23", "$", "$", "L", By.ID)
TM.add_transition("32", "8", "0", "*", "L", By.ID)
TM.add_transition("32", "7", "1", "*", "L", By.ID)
