import utils
from state import State
from utils import pretty_print_timetable
from check_constraints import check_mandatory_constraints

Result = tuple[bool, int, int, State]

def hill_climbing(initial: State, max_iters: int = 1000) -> Result:
    iters, states = 0, 0
    state = initial.clone()
    
    while iters < max_iters:
        iters += 1
        print(iters)
        print(state.materii_ramase)
        
        # Găsim cea mai bună stare vecină și, 
        # dacă este mai bună decât cea curentă, continuăm din acea stare.
        # Nu uitați să adunați numărul de stări construite.
        successors = state.get_next_states()
        successors = list(sorted(successors, key=lambda x: x.conflicts()))
        print("conflicts - ", state.conflicts())

        if not successors:
            break

        succ = successors[0]
        states += len(successors)
        
        if succ.score() >= state.score():
            break
        else:
            state = succ.clone()
        
    return state.is_final(), iters, states, state

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
    state_init.materii_ramase = dict(sorted(state_init.materii_ramase.items(),
                                             key=lambda x: (profi_materie(x[0], timetable_specs[utils.PROFESORI]), x[0])))
        
    # Aplică algoritmul Hill Climbing
    result = hill_climbing(state_init)

    # Afișează rezultatul
    result[3].display()
    print("stare finala - ", result[0])

    return result