import utils
import random
from state import State
from utils import pretty_print_timetable
from check_constraints import check_mandatory_constraints

Result = tuple[bool, int, int, State]

def stochastic_hill_climbing(initial: State, max_iters: int = 1000) -> tuple[bool, State]:
    iters, states = 0, 0
    state = initial.clone()
    
    while iters < max_iters:
        iters += 1
        print(" iter - ", iters)
        
        # Alegem aleator între vecinii mai buni decât starea curentă.
        successors = state.get_next_actions()
        states += len(successors)

        if len(successors) == 0:
            break
        
        min_conflict = min(map(lambda x: x[1], successors))
        better_succ = list(filter(lambda x: x[1] == min_conflict, successors))
        
        if len(better_succ) == 0:
            break
        else:
            next_succ = random.choice(better_succ)
            state.apply_action(next_succ[0], next_succ[1])

    return state.is_final(), state

def random_restart_hill_climbing(
    initial: State,
    max_restarts: int = 30, 
    run_max_iters: int = 100, 
) -> Result:
    
    total_iters, total_states = 0, 0
    
    # Realizăm maximum max_restarts căutări de tip Hill Climbing.
    state = initial.clone()
    end_state = state
    restarts = 0
    
    while restarts < max_restarts:
        restarts += 1
        print("restarts - ", restarts)

        is_final, final_state = stochastic_hill_climbing(state, max_iters=run_max_iters)

        if is_final and final_state.conflicts() == 0:
            return is_final, total_iters, total_states, final_state
        
        print("conflicts - ", final_state.conflicts())
        if (final_state.conflicts() <= end_state.conflicts() or end_state == state) and is_final:
            end_state = final_state
        
    return end_state.is_final(), total_iters, total_states, end_state

def profi_materie(materie, profesori) -> int:
    score = 0
    for profesor in profesori:
        if materie in profesori[profesor][utils.MATERII]:
            score += 1
    return score

def hill_climbing_algorithm_function(filename: str, timetable_specs: dict):
    state_init = State(filename=filename,
                       materii=timetable_specs[utils.MATERII],
                       profesori=timetable_specs[utils.PROFESORI],
                       sali=timetable_specs[utils.SALI],
                       zile=timetable_specs[utils.ZILE],
                       intervale=timetable_specs[utils.INTERVALE])
    
    # Sortează materiile după numărul de profesori și numărul de studenți asignați
    # state_init.materii_ramase = dict(sorted(state_init.materii_ramase.items(),
    #                                          key=lambda x: (profi_materie(x[0], timetable_specs[utils.PROFESORI]), x[0])))
        
    # Aplică algoritmul Hill Climbing
    # result = hill_climbing(state_init)

    result = random_restart_hill_climbing(state_init)

    # Afișează rezultatul
    result[3].display()
    print("stare finala - ", result[0])

    return result