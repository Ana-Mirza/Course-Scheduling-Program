import utils
import check_constraints
from heapq import heappop, heappush
from state import State

from time import time

# Implementarea algoritmului A* cu IDA*
def astar_ida(start, end, h, h_max):
    # Frontiera, ca listă (heap) de tupluri (cost_f, nod)
    frontier = []
    heappush(frontier, (0 + h(start, end), start))
    
    # Nodurile descoperite ca dicționar nod -> cost_g-până-la-nod
    discovered = {start: 0}
    states = 0

    # Implementăm algoritmul A*
    while frontier:
        _, current = heappop(frontier)

        if current.is_final():
          break

        # explore neighbors
        successors = current.get_next_states()
        states += len(successors)
        filtered_succ = list(filter(lambda x: g(x, start) + h(x, end) < h_max, successors))
        eliminated_succ = list(filter(lambda x: g(x, start) + h(x, end) >= h_max, successors))

        # Calculăm f-ul maxim următor dintre vecinii eliminați
        if len(eliminated_succ) > 0:
            min_f = min(map(lambda x: g(x, start) + h(x, end), eliminated_succ))      
        else:
            min_f = h_max      

        # Explorăm vecinii care au f-ul mai mic decât f_max
        for neigh in filtered_succ:
            g_cost = g(neigh, start)

            if (neigh not in discovered) or (g_cost < discovered[neigh]):
                discovered[neigh] = g_cost
                heappush(frontier, (g_cost + h(neigh, end), neigh))

    return current, states, len(discovered.keys()), min_f # starea finala și numărul de stări descoperite

# Implementarea algoritmului IDA*
def ida(start, end, h):
    f_max = h(start, end)

    while True:
        result, num_states, explored_states, f_max = astar_ida(start, end, h, f_max)
        if result.is_final():
            return result, num_states, explored_states


# Implementarea algoritmului Memory Bounded A*
def memory_bound_astar(start, end, h):
    # Frontiera, ca listă (heap) de tupluri (cost_f, nod)
    frontier = []
    heappush(frontier, (0 + h(start, end), start))
    
    # Nodurile descoperite ca dicționar nod -> cost_g-până-la-nod
    discovered = {start: 0}
    states = 0

    # Implementăm algoritmul A*
    while frontier:
        _, current = heappop(frontier)

        if current.is_final():
          break

        # Verificăm dacă mai avem memorie -- limita este de 200000 de stări
        if len(frontier) > 200000:
            continue

        # Explorăm vecinii
        successors = current.get_next_states()
        states += len(successors)

        # Sortăm vecinii după costul g și alegem primii 100 (memory bounded A*)
        sorted_succ = sorted(successors, key=lambda x: g(x, start))

        for neigh in sorted_succ[:100]:
            g_cost = g(neigh, start)

            if (neigh not in discovered) or (g_cost < discovered[neigh]):
                discovered[neigh] = g_cost
                heappush(frontier, (g_cost + h(neigh, end), neigh))

    return current, states, len(discovered.keys()) # starea finala și numărul de stări descoperite


# Funcție ce calculează numărul de profesori disponibili pentru o materie
def profi_materii(materii_ramase, profesori) -> int:
    score = 0

    for materie in materii_ramase:
        num_profi = 0
        for profesor in profesori:
            if materie in profesori[profesor][utils.MATERII] and profesori[profesor][utils.INTERVALE] < 7:
                num_profi += 1
        score += num_profi * materii_ramase[materie]

    return score

# Funcție ce calculează numărul de studenți rămași de alocat
def students_left(materii) -> int:
    students = 0
    for materie in materii:
        students += materii[materie]

    return students

# Funcție euristică pentru A* și IDA*
def h(start: State , end: list[str]):
   if len(start.materii_ramase) == len(end):
       return 0
   
   # ponderi pentru costul euristicii
   w_students = 0.1
   w_profi = 0.001
   
   cost = w_students * students_left(start.materii_ramase) + w_profi * profi_materii(start.materii_ramase, start.profesori)
   return cost

# Funcție de cost pentru A* și IDA*
def g(current: State, start: State):
    # pondere pentru costul g
    w = h(start, []) + 1

    return current.conflicts() * w


def astar_algorithm_function(filename: str, timetable_specs: dict):
    state_init = State(filename=filename,
                       materii=timetable_specs[utils.MATERII],
                       profesori=timetable_specs[utils.PROFESORI],
                       sali=timetable_specs[utils.SALI],
                       zile=timetable_specs[utils.ZILE],
                       intervale=timetable_specs[utils.INTERVALE])
    
    # Memory Bound A*
    # start_time = time()
    # result_state, num_state, explored_states = memory_bound_astar(state_init, [], h)
    # end_time = time()

    # Scriem rezultatul în fișierul de ieșire
    # filename = filename.split('.')[0] + '.txt'
    # filename = 'mbastar_outputs/' + filename.split('/')[-1]
    # with open(filename, 'w') as f:
    #     f.write(utils.pretty_print_timetable(result_state.orar, result_state.filename))
    #     f.write("Numarul de stari: " + str(num_state) + "\n")
    #     f.write("Cost: " + str(result_state.conflicts()))

    # IDA*
    start_time = time()
    result_state, num_state, explored_states = ida(state_init, [], h)
    end_time = time()

    # Scriem rezultatul în fișierul de ieșire
    filename = filename.split('.')[0] + '.txt'
    filename = 'astar_outputs/' + filename.split('/')[-1]
    with open(filename, 'w') as f:
        f.write(utils.pretty_print_timetable(result_state.orar, result_state.filename))
        f.write("Numarul de stari: " + str(num_state) + "\n")
        f.write("Cost: " + str(result_state.conflicts()))

    # Printăm rezultatul în consolă
    result_state.display()
    print("Numarul de stari construite: " + str(num_state))
    print("Numarul de stari explorate: " + str(explored_states))
    print("Cost: " + str(result_state.conflicts()))
    print("Timp de rulare: " + str(end_time - start_time) + " sec")

    return result_state
