import utils
import check_constraints
from heapq import heappop, heappush
from state import State

def astar(start, end, h):
    # Frontiera, ca listă (heap) de tupluri (cost_f, nod)
    frontier = []
    heappush(frontier, (0 + h(start, end), start))
    
    # Nodurile descoperite ca dicționar nod -> (părinte, cost_g-până-la-nod)
    discovered = {start: 0}

    # Implementăm algoritmul A*
    while frontier:
        # TODO
        _, current = heappop(frontier)
        print("frontier size", len(frontier))
        print("current", current.materii_ramase)

        if current.is_final():
          break

        # explore neighbors
        successors = current.get_next_states()
        print("numarul de vecini", len(successors))
        for neigh in successors:
            g_cost = neigh.conflicts() * 100

            if (neigh not in discovered) or (g_cost < discovered[neigh]):
                if neigh in discovered:
                    print("discovered with g_cost", discovered[neigh])
                    print("current g_cost", g_cost)
                discovered[neigh] = g_cost
            #   print("g_cost", g_cost)
            #   print("h_cost", h(neigh, end))
                heappush(frontier, (g_cost + h(neigh, end), neigh))

    return current, len(discovered.keys()) # starea finala și numărul de stări descoperite


# Euristic function
def profi_materii(materii_ramase, profesori) -> int:
    score = 0

    for materie in materii_ramase:
        num_profi = 0
        for profesor in profesori:
            if materie in profesori[profesor][utils.MATERII] and profesori[profesor][utils.INTERVALE] < 7:
                num_profi += 1
        score += num_profi * materii_ramase[materie]

    return score

def students_left(materii) -> int:
    students = 0
    for materie in materii:
        students += materii[materie]

    return students

def h(start: State , end: list[str]):
   if len(start.materii_ramase) == len(end):
       return 0
   
#    cost = profi_materie(list(start.materii_ramase.keys())[0], start.profesori)
#    cost = students_left(start.materii_ramase) / 1000
   cost = profi_materii(start.materii_ramase, start.profesori) / 1000 
   print(cost)
   return cost


def astar_algorithm_function(filename: str, timetable_specs: dict):
    state_init = State(filename=filename,
                       materii=timetable_specs[utils.MATERII],
                       profesori=timetable_specs[utils.PROFESORI],
                       sali=timetable_specs[utils.SALI],
                       zile=timetable_specs[utils.ZILE],
                       intervale=timetable_specs[utils.INTERVALE])
    
    result_state, num_state = astar(state_init, [], h)
    result_state.display()
    print("Numarul de stari: ", num_state)
    print("Stare finala: ", result_state.is_final())

    return result_state
