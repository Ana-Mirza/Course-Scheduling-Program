from utils import pretty_print_timetable
from check_constraints import parse_interval
from ast import literal_eval
from copy import deepcopy
import json

##################### MACROURI #####################
SLOTURI = 'Sloturi'
MATERII = 'Materii'
CAPACITATE = 'Capacitate'
INTERVALE = 'Intervale'
CONSTRANGERI ='Constrangeri'

class State:
    def __init__(
            self,
            filename: str,
            materii: dict[str, int],
            profesori: dict[str, dict[str, int | list[str] | list[tuple[int, int]]]],
            sali: dict[str, dict[str, list[str] | int]],
            orar: dict[str, dict[tuple[int, int], dict[str, tuple[str, str]]]] | None = None, 
            conflicte: int | None = None,
            zile: list[str] | None = None,
            intervale: list[tuple[int, int]] | None = None
    ) -> None:
        # Crează orar populat cu datele de intrare
        self.orar = orar if orar is not None else State.generate_orar(zile, intervale, sali)
        self.conflicte = conflicte if conflicte is not None else 0
        self.materii_ramase = materii
        self.profesori = profesori
        self.sali = sali
        self.filename = filename

        # Crează listă de sloturi ocupate pentru fiecare profesor
        for profesor in self.profesori:
            if SLOTURI not in self.profesori[profesor]:
                self.profesori[profesor][SLOTURI] = {}
            if INTERVALE not in self.profesori[profesor]:
                self.profesori[profesor][INTERVALE] = 0

    def __hash__(self):
        # return hash(json.dumps(self.orar, sort_keys=True))
        # return hash(frozenset(self.orar.items()))

        return hash(str(self.orar))

        # if self.orar is None:
        #     return hash(None)

        # hash_result = 0
        # for key, value in self.orar.items():
        #     hash_result ^= hash(key)  # Adăugăm la hash cheia principală
        #     for inner_key, inner_value in value.items():
        #         hash_result ^= hash(inner_key)  # Adăugăm la hash cheia din interior
        #         hash_result ^= hash(frozenset(inner_value.items()))  # Adăugăm la hash valorile
        # return hash_result

    def students_left(self, materii) -> int:
        students = 0
        for materie in materii:
            students += materii[materie]

        return students
    
    def __lt__(self, other):
        # Defines the less than comparison logic
        # return len(self.materii_ramase) < len(other.materii_ramase)
        return self.students_left(self.materii_ramase) < self.students_left(other.materii_ramase)
    
    def __gt__(self, other):
        # Defines the greater than comparison logic
        # return len(self.materii_ramase) > len(other.materii_ramase)
        return self.students_left(self.materii_ramase) > self.students_left(other.materii_ramase)
    
    def __eq__(self, other):
        # Defines the equality logic
        # return self.conflicte == other.conflicte
        return self.students_left(self.materii_ramase) == self.students_left(other.materii_ramase)

    @staticmethod
    def generate_orar(zile: list[str],
                    intervale: list[tuple[int, int]],
                    sali: dict[str, dict[str, str | int]]) -> dict[str, dict[tuple[int, int], dict[str, tuple[str, str]]]]:
        '''
        Construiește un orar inițial gol.
        '''

        orar = {}
        for zi in zile:
            orar[zi] = {}
            for interval in intervale:
                interval = literal_eval(interval)
                orar[zi][interval] = {}
                for sala in sali:
                    orar[zi][interval][sala] = None

        return orar
    
    def is_final(self) -> bool:
        """
        Întoarce True dacă este stare finală.
        Starea este finală când am asignat slot pentru fiecare materie.
        """
        return len(self.materii_ramase) == 0
    
    def get_next_actions(self):
        '''
        Întoarce toate posibilele stări următoare.
        '''
        next_actions = []
        # parcurge toate intervalele orare goale și încearcă să le umple cu materiile rămase
        for zi in self.orar:
            for interval in self.orar[zi]:
                for sala in self.orar[zi][interval]:
                    if not self.orar[zi][interval][sala]:
                        for materie in self.materii_ramase:
                            # Verifică dacă materia poate fi ținută în sala respectivă
                            if materie not in self.sali[sala][MATERII]:
                                continue

                            # Găsește profesor care să țină materia
                            for profesor in self.profesori:
                                if materie not in self.profesori[profesor][MATERII]:
                                    continue

                                # Verifică dacă profesorul mai poate preda
                                if self.profesori[profesor][INTERVALE] == 7:
                                    continue
                                # Verifică dacă profesorul are slotul liber
                                if zi in self.profesori[profesor][SLOTURI] and interval in self.profesori[profesor][SLOTURI][zi]:
                                    continue

                                #####################################
                                # Crează stare vecină noua
                                next_state = self.clone()
                                next_state.orar[zi][interval][sala] = (profesor, materie)

                                # Updatează orarul profesorului
                                next_state.profesori[profesor][INTERVALE] += 1
                                if zi not in next_state.profesori[profesor][SLOTURI]:
                                    next_state.profesori[profesor][SLOTURI][zi] = []
                                next_state.profesori[profesor][SLOTURI][zi].append(interval)

                                # Calculează numărul de conflite soft încălcate
                                next_state.conflicte = State.__compute_conflicts(orar=next_state.orar, profesori=next_state.profesori)

                                # Updatează numărul de stundeți rămași cu materia respectivă
                                next_state.materii_ramase[materie] -= self.sali[sala][CAPACITATE]

                                # Elimină materia din lista celor rămase dacă a fost acoperită în totalitate
                                if next_state.materii_ramase[materie] <= 0:
                                    next_state.materii_ramase.pop(materie)
                                #####################################
                                
                                # Adaugă starea vecină în lista de stări următoare
                                # next_states.append(next_state)

                                # Crează listă de acțiuni posibile
                                action = (zi, interval, sala, profesor, materie)
                                action_conflicts = State.__compute_conflicts2(action, self.profesori[profesor][CONSTRANGERI])
                                
                                next_actions.append((action, action_conflicts))
        # return next_states
        return next_actions
    
    def get_next_states(self):
        '''
        Întoarce toate posibilele stări următoare.
        '''
        next_states = []
        next_actions = []
        # parcurge toate intervalele orare goale și încearcă să le umple cu materiile rămase
        for zi in self.orar:
            for interval in self.orar[zi]:
                for sala in self.orar[zi][interval]:
                    if not self.orar[zi][interval][sala]:
                        for materie in self.materii_ramase:
                            # Verifică dacă materia poate fi ținută în sala respectivă
                            if materie not in self.sali[sala][MATERII]:
                                continue

                            # Găsește profesor care să țină materia
                            for profesor in self.profesori:
                                if materie not in self.profesori[profesor][MATERII]:
                                    continue

                                # Verifică dacă profesorul mai poate preda
                                if self.profesori[profesor][INTERVALE] == 7:
                                    continue
                                # Verifică dacă profesorul are slotul liber
                                if zi in self.profesori[profesor][SLOTURI] and interval in self.profesori[profesor][SLOTURI][zi]:
                                    continue

                                #####################################
                                # Crează stare vecină noua
                                next_state = self.clone()
                                next_state.orar[zi][interval][sala] = (profesor, materie)

                                # Updatează orarul profesorului
                                next_state.profesori[profesor][INTERVALE] += 1
                                if zi not in next_state.profesori[profesor][SLOTURI]:
                                    next_state.profesori[profesor][SLOTURI][zi] = []
                                next_state.profesori[profesor][SLOTURI][zi].append(interval)

                                # Calculează numărul de conflite soft încălcate
                                next_state.conflicte = State.__compute_conflicts(orar=next_state.orar, profesori=next_state.profesori)

                                # Updatează numărul de stundeți rămași cu materia respectivă
                                next_state.materii_ramase[materie] -= self.sali[sala][CAPACITATE]

                                # Elimină materia din lista celor rămase dacă a fost acoperită în totalitate
                                if next_state.materii_ramase[materie] <= 0:
                                    next_state.materii_ramase.pop(materie)
                                #####################################
                                
                                # Adaugă starea vecină în lista de stări următoare
                                next_states.append(next_state)
        return next_states
    
    def apply_action(self, action: tuple[str, str, str, str, str], conflicts: int):
        '''
        Aplică o acțiune asupra stării curente.
        '''
        zi, interval, sala, profesor, materie = action

        # Updatează orarul
        self.orar[zi][interval][sala] = (profesor, materie)

        # Updatează orarul profesorului
        self.profesori[profesor][INTERVALE] += 1
        if zi not in self.profesori[profesor][SLOTURI]:
            self.profesori[profesor][SLOTURI][zi] = []
        self.profesori[profesor][SLOTURI][zi].append(interval)

        # Calculează numărul de conflite soft încălcate
        self.conflicte += conflicts

        # Updatează numărul de stundeți rămași cu materia respectivă
        self.materii_ramase[materie] -= self.sali[sala][CAPACITATE]

        # Elimină materia din lista celor rămase dacă a fost acoperită în totalitate
        if self.materii_ramase[materie] <= 0:
            self.materii_ramase.pop(materie)
    
    @staticmethod
    def __compute_conflicts2(action: tuple[str, str, str, str, str], 
                             constrangeri_prof: dict[str, str]) -> int:
        """
        Calculează numărul de conflicte cauzate de această acțiune.
        """

        zi, interv, _, _, _ = action
        constrangeri = 0

        for const in constrangeri_prof:
            if const[0] != '!':
                continue

            const = const[1:]

            # Verifică constrângerile de zile
            if const in ['Luni', 'Marti', 'Miercuri', 'Joi', 'Vineri']:
                if const == zi:
                    constrangeri += 1

            # Verifică constrângerile de intervale
            else:
                interval = parse_interval(const)
                start, end = interval

                if start != end - 2:
                    intervals = [(i, i + 2) for i in range(start, end, 2)]
                else:
                    intervals = [(start, end)]

                for interval in intervals:
                    if interv == interval:
                        constrangeri += 1
                        
        return constrangeri
    
    @staticmethod
    def __compute_conflicts(orar: dict[str, dict[tuple[int, int], dict[str, tuple[str, str]]]],
                             profesori: dict[str, dict[str, int | list[str] | list[tuple[int, int]]]]) -> int:
        '''
        Calculează numărul de conflicte din această stare.
        '''
        constrangeri = 0
        for prof in profesori:
            for const in profesori[prof][CONSTRANGERI]:
                if const[0] != '!':
                    continue

                const = const[1:]

                # Verifică constrângerile de zile
                if const in orar:
                    zi = const

                    if zi in profesori[prof][SLOTURI]:
                        constrangeri += len(profesori[prof][SLOTURI][zi])

                # Verifică constrângerile de intervale
                else:
                    interval = parse_interval(const)
                    start, end = interval

                    if start != end - 2:
                        intervals = [(i, i + 2) for i in range(start, end, 2)]
                    else:
                        intervals = [(start, end)]

                    for interval in intervals:
                        for zi in profesori[prof][SLOTURI]:
                            if interval in profesori[prof][SLOTURI][zi]:
                                constrangeri += 1
        return constrangeri
    
    def conflicts(self) -> int:
        '''
        Întoarce numărul de conflicte din această stare.
        '''
        return self.conflicte
    
    def score(self) -> int:
        '''
        Întoarce numărul de studenți rămași neasignați.
        '''
        scor = 0
        for materie in self.materii_ramase:
            scor += self.materii_ramase[materie]

        return scor
    
    def display(self) -> None:
        '''
        Afișează orarul.
        '''
        print(pretty_print_timetable(self.orar, self.filename))

    def clone(self):
        '''
        Clonează starea curentă.
        '''
        return deepcopy(self)
