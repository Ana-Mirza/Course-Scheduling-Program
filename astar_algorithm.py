import utils
import check_constraints

def astar_algorithm_function(filename: str):
    timetable_specs = utils.read_yaml_file(filename)
    print(timetable_specs)