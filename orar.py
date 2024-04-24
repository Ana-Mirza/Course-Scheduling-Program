import sys
from astar_algorithm import astar_algorithm_function  # importați funcția pentru algoritmul A* sau algoritmul Hill Climbing
from hill_climbing_algorithm import hill_climbing_algorithm_function  # importați funcția pentru algoritmul Hill Climbing

def main(algorithm, input_file):
    # Implementați logica pentru citirea și procesarea fișierului de intrare
    # Apelați algoritmul corespunzător în funcție de argumentul algoritmului

    if algorithm == "astar":
        # Apelați funcția pentru algoritmul A* și salvați rezultatul într-o variabilă
        result = astar_algorithm_function(input_file)
    elif algorithm == "hc":
        # Apelați funcția pentru algoritmul Hill Climbing și salvați rezultatul într-o variabilă
        result = hill_climbing_algorithm_function(input_file)
    else:
        print("Algoritmul specificat nu este recunoscut.")
        return

    # Afișați soluția la ieșire (pretty-printed)
    print("Soluția este:")
    print(result)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python orar.py <algorithm> <input_file>")
        sys.exit(1)

    algorithm = sys.argv[1]
    input_file = sys.argv[2]

    main(algorithm, input_file)
