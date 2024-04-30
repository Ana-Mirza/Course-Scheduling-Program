import sys
from astar_algorithm import astar_algorithm_function
from hill_climbing_algorithm import hill_climbing_algorithm_function
from check_constraints import check_mandatory_constraints
from check_constraints import check_optional_constraints
from utils import read_yaml_file

def main(algorithm, input_file):
    # Procesarea fișierului de intrare
    timetable_specs = read_yaml_file(input_file)

    if algorithm == "astar":
        # Apelarea funcției pentru algoritmul A* și salvarea rezultatului într-o variabilă
        result = astar_algorithm_function(input_file, timetable_specs)
        result_state = result
    elif algorithm == "hc":
        # Apelarea funcției pentru algoritmul Hill Climbing și salvarea rezultatului într-o variabilă
        result = hill_climbing_algorithm_function(input_file, timetable_specs)
        result_state = result[3]
    else:
        print("Algoritmul specificat nu este recunoscut.")
        return
    
    # Verificăm rezultatul obținut
    check_mandatory_constraints(result_state.orar, timetable_specs)
    check_optional_constraints(result_state.orar, timetable_specs)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python orar.py <algorithm> <input_file>")
        sys.exit(1)

    algorithm = sys.argv[1]
    input_file = sys.argv[2]

    main(algorithm, input_file)
