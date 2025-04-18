# Timetable Generator using AI Search Algorithms

This project implements a timetable (schedule) generator that adheres to both physical and preferential constraints. It uses Artificial Intelligence search algorithms—specifically **A\*** and a modified version of **Hill Climbing**—to find feasible and optimized timetables.

The project was developed as part of an academic assignment for the **Artificial Intelligence course**.

## 🧠 Algorithms Used

- **A\*** Search: A heuristic-based search algorithm that explores the most promising paths to find an optimal timetable.
- **Hill Climbing** (modified): A local search algorithm adapted for this problem to iteratively improve the schedule until a (possibly local) optimum is reached.

Each algorithm is tailored to fit the constraints and structure of the timetable generation problem, including:
- No overlapping sessions
- Fixed room and group assignments
- Time availability constraints
- Optional preferences (e.g., minimizing breaks)

## 📁 Folder Structure

```
.
├── orare.py              # Main script for running the algorithms
├── inputs/               # Contains .yaml files with input data (rooms, courses, professors, etc.)
├── outputs/              # (Optional) Where generated timetables can be saved
└── README.md             # This file
```

## 🛠️ How to Use

Make sure you have **Python 3** installed.

Run the script from the command line as follows:

```bash
$ python3 orare.py <algorithm> <input_file>.yaml
```

### Arguments:

* ``<algorithm>`` – Choose either hc (for Hill Climbing) or astar (for A* Search).

* ``<input_file>.yaml`` – Path to the YAML file containing the problem setup (in the inputs/ folder).

### Example:

```bash
$ python3 orare.py hc inputs/sample_input.yaml
```

This will generate a timetable using Hill Climbing based on the ``sample_input.yaml`` configuration.

## 📄 Input Format
Each YAML input file describes:

* The available rooms

* Groups of students

* Courses and professors

* Constraints such as time slots and availability

Refer to the examples in the inputs/ folder to understand the format and how to create your own.

## 📊 Output
The generated timetable is displayed in the terminal. Optionally, it can be saved to a file or extended with visualization support.

## 📚 Report
For a deeper understanding of the problem formulation, algorithm adaptations, and performance comparison, check out the full project report: ``Tema1_IA_Orare.pdf``.
