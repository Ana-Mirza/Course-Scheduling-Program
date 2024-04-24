from utils import pretty_print_timetable
from utils import parse_interval
from state import State

##################### MACROURI #####################
SLOTURI = 'Sloturi'
MATERII = 'Materii'
CAPACITATE = 'Capacitate'
INTERVALE = 'Intervale'

class State:
    def __init__(
            self,
            materii: dict[str, int],
            profesori: dict[str, dict[str, list[str]]],
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

        # Crează listă de sloturi ocupate pentru fiecare profesor
        for profesor in self.profesori:
            if SLOTURI not in self.profesori[profesor]:
                self.profesori[profesor][SLOTURI] = {}
            if INTERVALE not in self.profesori[profesor]:
                self.profesori[profesor][INTERVALE] = 0


    @staticmethod
    def generate_orar(zile: list[str],
                    intervale: list[tuple[int, int]],
                    sali: dict[str, dict[str, str | int]]) -> dict[str, dict[(int, int), dict[str, (str, str)]]]:
        '''
        Construiește un orar inițial gol.
        '''

        orar = {}
        for zi in zile:
            orar[zi] = {}
            for interval in intervale:
                orar[zi][interval] = {}
                for sala in sali:
                    orar[zi][interval][sala] = ('', '')

        return orar
    
    def is_final(self) -> bool:
        """
        Întoarce True dacă este stare finală.
        """
        return len(self.materii_ramase) == 0
    
    def get_next_states(self) -> list[State]:
        '''
        Întoarce toate posibilele stări următoare.
        '''
        next_states = []
        # parcurge toate intervalele orare goale și încearcă să le umple cu materiile rămase
        for zi in self.orar:
            for interval in self.orar[zi]:
                for sala in self.orar[zi][interval]:
                    if self.orar[zi][interval][sala] == ('', ''):
                        for materie in self.materii_ramase:
                            # Verifică dacă materia poate fi ținută în sala respectivă
                            if materie not in self.sali[sala][MATERII]:
                                continue

                            # Găsește profesor care să țină materia
                            for profesor in self.profesori:
                                if materie not in self.profesori[profesor][MATERII]:
                                    continue

                                # Verifică dacă profesorul mai poate preda
                                if len(self.profesori[profesor][INTERVALE]) == 7:
                                    continue
                                # Verifică dacă profesorul are slotul liber
                                if zi in self.profesori[profesor][SLOTURI] and interval in self.profesori[profesor][SLOTURI][zi]:
                                    continue

                                # Crează stare vecină noua
                                next_state = self.clone()
                                next_state.orar[zi][interval][sala] = (materie, profesor)

                                # Calculează numărul de conflite soft încălcate
                                next_state.conflicte = State.__compute_conflicts(next_state.orar, next_state.profesori)

                                # Updatează orarul profesorului
                                self.profesori[profesor][INTERVALE] += 1
                                if zi not in self.profesori[profesor][SLOTURI]:
                                    self.profesori[profesor][SLOTURI][zi] = []
                                self.profesori[profesor][SLOTURI][zi].append(interval)

                                # Updatează numărul de stundeți rămași cu materia respectivă
                                next_state.materii_ramase[materie] -= self.sali[sala][CAPACITATE]

                                # Elimină materia din lista celor rămase dacă a fost acoperită în totalitate
                                if next_state.materii_ramase[materie] <= 0:
                                    next_state.materii_ramase.pop(materie)
                                next_states.append(next_state)
        return next_states
    
    @staticmethod
    def __compute_conflicts(orar: dict[str, dict[tuple[int, int], dict[str, tuple[str, str]]]],
                             profesori: dict[str, dict[str, list[str]]]) -> int:
        '''
        Calculează numărul de conflicte din această stare.
        '''
        constrangeri = 0
        for prof in profesori:
            for const in profesori[prof]:
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
                            if interval in zi:
                                constrangeri += 1
        return constrangeri
    
    def conflicts(self) -> int:
        '''
        Întoarce numărul de conflicte din această stare.
        '''
        return self.conflicte
    
    def display(self) -> None:
        '''
        Afișează orarul.
        '''
        pretty_print_timetable(self.orar)

    def clone(self) -> State:
        '''
        Clonează starea curentă.
        '''
        
        return State(
            self.orar,
            self.conflicte,
            self.materii_ramase.copy(),
            self.profesori.copy(),
            self.sali.copy()
        )
