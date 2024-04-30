import utils
import random
from state import State

from time import time

Result = tuple[bool, int, int, State]

# Implementarea algoritmului Stochastic Hill Climbing
def stochastic_hill_climbing(initial: State, max_iters: int = 1000) -> tuple[bool, State]:
    iters, states = 0, 0
    state = initial.clone()
    
    while iters < max_iters:
        iters += 1
        
        # Alegem aleator între vecinii mai buni decât starea curentă.
        successors = state.get_next_actions()
        states += len(successors)

        if len(successors) == 0:
            break
        
        # Alegem un vecin aleator dintre cei cu cost minim
        min_conflict = min(map(lambda x: x[1], successors))
        better_succ = list(filter(lambda x: x[1] == min_conflict, successors))
        
        # Dacă nu mai avem vecini mai buni, ne oprim
        if len(better_succ) == 0:
            break
        else:
            next_succ = random.choice(better_succ)
            state.apply_action(next_succ[0], next_succ[1])

    return state.is_final(), state, states

# Implementarea algoritmului Random Restart Hill Climbing
def random_restart_hill_climbing(
    initial: State,
    max_restarts: int = 30, 
    run_max_iters: int = 100, 
) -> Result:
    
    _, total_states = 0, 0
    
    # Realizăm maximum max_restarts căutări de tip Hill Climbing.
    state = initial.clone()
    end_state = state
    restarts = 0
    
    while restarts < max_restarts:
        restarts += 1

        # Aplicăm algoritmul Stochastic Hill Climbing
        is_final, final_state, num_states = stochastic_hill_climbing(state, max_iters=run_max_iters)
        total_states += num_states

        # Dacă am găsit o soluție finală, o returnăm
        if is_final and final_state.conflicts() == 0:
            return is_final, restarts, total_states, final_state
        
        # Actualizăm starea finală dacă am găsit o soluție mai bună decât cea anterioară și continuăm căutarea
        if (final_state.conflicts() <= end_state.conflicts() or end_state == state) and is_final:
            end_state = final_state
        
    return end_state.is_final(), restarts, total_states, end_state

def hill_climbing_algorithm_function(filename: str, timetable_specs: dict):
    state_init = State(filename=filename,
                       materii=timetable_specs[utils.MATERII],
                       profesori=timetable_specs[utils.PROFESORI],
                       sali=timetable_specs[utils.SALI],
                       zile=timetable_specs[utils.ZILE],
                       intervale=timetable_specs[utils.INTERVALE])

    # Aplică algoritmul Random Restart Hill Climbing
    start_time = time()
    result = random_restart_hill_climbing(state_init)
    end_time = time()

    # Scriem rezultatul în fișier
    filename = filename.split('.')[0] + '.txt'
    filename = 'hc_outputs/' + filename.split('/')[-1]
    with open(filename, 'w') as f:
        f.write(pretty_print_timetable(result[3].orar, result[3].filename))
        f.write("Numarul de stari: " + str(result[2]) + "\n")
        f.write("Numarul de restarts: " + str(result[1]) + "\n")
        f.write("Cost: " + str(result[3].conflicts()))

    # Printăm rezultatul în consolă
    result[3].display()
    print("Numarul de stari: " + str(result[2]))
    print("Numarul de restarts: " + str(result[1]))
    print("Cost: " + str(result[3].conflicts()))
    print("Timp de rulare: " + str(end_time - start_time) + " sec")

    return result