*This project has been created as part of the 42 curriculum by yousenna.*



# Fly-In: Drone Fleet Simulation

<div align="center">
  <img src="fly-in_screenshote.svg" alt="Fly-in Project Screenshot" width="90%">
</div>


## Description

Fly-In is a Python-based simulation project that models the movement of a fleet of drones from a starting hub to a destination hub across a network of zones. The simulation reads a custom map file defining the environment, including zones with various properties (capacities, types) and the connections between them. The core of the project is an intelligent pathfinding algorithm that guides the drones turn by turn, optimizing for the shortest path while respecting zone capacities and connection constraints. The project features both a command-line output for turn-based moves and a real-time graphical visualization using Pygame.

The goal is to efficiently navigate all drones to the end hub in the minimum number of turns possible, avoiding collisions and respecting all environmental rules.

## Instructions

### Installation

This project uses Poetry for dependency management.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/youssenna/fly-in
    cd fly-in
    ```

2.  **Install dependencies:**
    Make sure you have Python 3.12+ and pip installed. Then, run the following command from the project root:
    ```bash
    make install
    ```
    This will create a virtual environment and install all required packages listed in `pyproject.toml`.

### Execution

You can run the simulation in two modes: standard output or visualizer.

*   **Standard Mode:**
    To run the simulation and print the drone moves for each turn to the console:
    ```bash
    poetry run python main.py <path/to/map_file.txt>
    ```

*   **Visualizer Mode:**
    To launch the graphical interface and watch the simulation in real-time:
    ```bash
    poetry run python main.py <path/to/map_file.txt> --visual
    ```
    You can also use the provided Makefile shortcut to run visual mode of chalanger map:
    ```bash
    make run
    ```

*   **Debugging:**
    To run the simulation with the PDB debugger for chalanger map:
    ```bash
    make debug
    ```
    or if you want speciphic file:
    ```bash
    poetry run python -m pdb main.py <path/to/map_file.txt> --visual
    ```

## Algorithm Choices and Implementation Strategy

The core of the drone navigation logic revolves around a modified Dijkstra's algorithm to find the shortest path for each drone on every turn.

### Pathfinding Algorithm

-   **Dijkstra's Algorithm**: At each turn, for every drone not yet at the destination, the simulation calculates the shortest path from its current zone to the `end_hub`. The `shortest_path_between_zones` method implements this.
-   **Cost Function**: The "cost" of traversing a zone is determined by its type. `Normal` zones have a cost of 1, while `restricted` zones have a higher cost of 2, making them less preferable. `Blocked` zones have an infinite cost and are impassable.
-   **Dynamic Pathfinding**: The path is not calculated just once. It is re-evaluated every turn for each drone. This allows the system to adapt to changing conditions, such as other drones occupying zones or connections.
-   **Constraint Handling**: The algorithm is modified to dynamically filter out neighbors (next possible zones) based on real-time constraints:
    -   **Zone Capacity**: A drone cannot move to a zone that is already at its `max_drones` capacity.
    -   **Connection Capacity**: A drone cannot use a connection that is at its `max_link_capacity`.
    -   **Visited Zones**: To prevent loops, each drone maintains a list of `old_zones` it has visited. The pathfinding algorithm avoids these zones to ensure forward progress.

### Turn-Based Logic (`ft_turn`)

The simulation proceeds in discrete turns. In each turn:
1.  The capacity usage of all zones and connections is reset and recalculated based on current drone positions.
2.  The simulation iterates through each active drone (not at the end hub).
3.  If a drone is on a connection (e.g., `Z1-Z2`), it completes its move to the destination zone (`Z2`).
4.  If a drone is in a zone, it invokes the pathfinding algorithm to find the best next move towards the end hub.
5.  If a valid path is found, the drone moves to the first zone in that path. The move is recorded, and the drone's state (current zone, capacity usage) is updated immediately to influence the decisions of subsequent drones in the same turn.

## Visual Representation Features

The visualizer, built with Pygame, provides an intuitive and engaging way to understand the simulation's progress.

-   **Real-Time Visualization**: Drones are rendered on the screen, moving between zones and along connections, providing immediate feedback on the algorithm's decisions.
-   **Zone Representation**:
    -   Zones are drawn as circles.
    -   Colors indicate the zone type (`blue` for normal, `purple` for restricted, `black` for blocked) or status (`green` for start/end hubs, `red` for isolated zones).
    -   Each zone displays its name, current drone count, and total capacity.
-   **Drone Representation**:
    -   Drones are represented by a custom image.
    -   When multiple drones are in a zone, their IDs are displayed.
    -   Drones traversing a connection are shown at the midpoint of the connection line.
-   **Interactive Controls**:
    -   **Spacebar**: Advances the simulation by one turn.
    -   **Down Arrow**: Resets the simulation, moving all drones back to the start hub.
    -   **Tab**: move map to left.

This graphical feedback makes it much easier to debug the algorithm, identify bottlenecks, and appreciate the complexity of the drone coordination.

## Resources

The core logic, algorithm design, and overall architecture of this project were developed by the author. An AI programming assistant was utilized as a tool to help with specific, well-defined tasks under the author's direction.

-   **AI-Assisted Tasks**:
    -   **Docstring Generation**: The AI was prompted to generate docstrings for existing classes and methods, which were then reviewed and integrated by the author. This helped accelerate the documentation process while ensuring compliance with coding standards.
    -   **README.md Scaffolding**: The AI was used to help structure and generate boilerplate text for this README file based on an analysis of the source code and a set of explicit requirements provided by the author. The author then refined and finalized the content.

-   **Useful Links**:
    -   [Pygame Documentation](https://www.pygame.org/docs/)
    -   [Dijkstra's Algorithm - Wikipedia](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
    -   [Dijkstra's Algorithm - free code camp](https://www.freecodecamp.org/news/dijkstras-shortest-path-algorithm-visual-introduction/)
    
    -   [Poetry Documentation](https://python-poetry.org/docs/)

## Author

<div align="center">
  <a href="https://github.com/youssenna">
    <img src="https://github.com/youssenna.png?size=150" alt="Youssef Ennajar" width="150" height="150" style="border-radius:50%;">
  </a>
  <h3>Youssef Ennajar (yousenna)</h3>
  <p>
    <a href="https://github.com/youssenna" target="_blank">GitHub</a> |
    <a href="https://www.linkedin.com/in/youssef-ennajar-213985253/" target="_blank">LinkedIn</a> |
    <a href="https://www.youtube.com/@codingwithmoljlaba" target="_blank">YouTube</a>
  </p>
</div>
