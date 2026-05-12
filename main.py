#!/usr/bin/env run

# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  main.py                                           :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: yousenna <yousenna@student.42.fr>         +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/03/30 16:47:56 by yousenna        #+#    #+#               #
#  Updated: 2026/05/12 18:39:14 by yousenna        ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

from typing import Dict, List, Union
from parser import Parser, Zone, Connection, ZoneTypes, Drone
from sys import argv, exit
from collections import deque
from math import inf


class Graph:
    """Represents the map as a graph of zones and connections."""
    def __init__(self, nb_drones: int, zones: Dict[str, Zone],
                 connections: List[Connection],
                 start_end_zones: Dict[str, str]):
        """
        Initializes the graph with all map data.

        Args:
            nb_drones: Number of drones in the simulation.
            zones: A dictionary of all zones in the map.
            connections: A list of all connections between zones.
            start_end_zones: A dict with start and end hub names.
        """
        self.nb_drones: int = nb_drones
        self.connections: Dict[str, Connection] = {
            con.zone1.name+'-'+con.zone2.name: con for con in connections
        }
        self.zones: Dict[str, Zone] = zones
        self.start_end_zones: Dict[str, str] = start_end_zones
        self.drones: deque[Drone] = self._creat_drones(nb_drones)
        self.paths: List[List[Zone]] = []
        self.path: List[Zone] = []
        self.distance: Dict[List[str], Graph.NodeInfo] = {}

    def _find_nighbors(self, zone_name: str) -> List[Zone]:
        """
        Finds all neighboring zones for a given zone.

        Args:
            zone_name: The name of the zone to find neighbors for.

        Returns:
            A list of neighboring Zone objects.
        """
        return [
            self.connections[connec].zone2 for connec in self.connections
            if self.connections[connec].zone1.name == zone_name
        ]

    def find_nighbors_for_every_zone(self) -> None:
        """
        Populates the neighbors list for every zone in the graph.
        """
        for zone in self.zones.values():
            zone.nighbors.extend(self._find_nighbors(zone.name))

    @staticmethod
    def _creat_drones(nb_drones: int) -> deque[Drone]:
        """
        Creates a deque of Drone objects.

        Args:
            nb_drones: The number of drones to create.

        Returns:
            A deque containing the initialized Drone objects.
        """
        return deque(Drone('D' + str(n+1)) for n in range(nb_drones))

    class NodeInfo:
        """
        A helper class to store pathfinding information for a zone i
        will use it in my shortest_path_between_zones method.
        """
        def __init__(self, cost: Union[float, int], previous_node: str):
            """
            Initializes the NodeInfo object.

            Args:
                cost: The cost to reach this node from the start.
                previous_node: The name of the previous node in the path.
            """
            self.cost: Union[float, int] = cost
            self.previous_node: str = previous_node

        def __str__(self) -> str:
            return f'cost = {self.cost} | previous node = {self.previous_node}'

        def __repr__(self) -> str:
            return self.__str__()

    def shortest_path_between_zones(
            self, start: Zone, end: Zone,
            old_zones: List[str], turn_zones: List[str]
            ) -> Dict[str, 'Graph.NodeInfo']:
        """
        Calculates the shortest path using Dijkstra's algorithm.

        It finds the shortest path between a start and end zone,
        avoiding specified old zones and considering drone traffic.

        Args:
            start: The starting zone.
            end: The destination zone.
            old_zones: A list of zones the drone has already visited.
            turn_zones: Zones involved in the current turn for traffic
                        avoidance logic.

        Returns:
            A dictionary mapping zone names to NodeInfo objects,
            representing the shortest path tree.
        """

        if start.name == end.name:
            return {}
        unvisited_zones: deque[str] = deque(self.zones.keys())
        distances: Dict[str, Graph.NodeInfo] = {
            zone: self.NodeInfo(inf, '') for zone in unvisited_zones
        }
        distances[start.name].cost = 0

        while unvisited_zones:
            unvisited_zones = deque(sorted(
                unvisited_zones,
                key=lambda x: (distances[x].cost,
                               self.zones[x].perfect)))
            target: str = unvisited_zones.popleft()
            # filter blocked_zones
            target_nighbors: List[Zone] = list(filter(
                lambda x: x.cost is not inf,
                self.zones[target].nighbors))

            # filter full zones and connection and old zones
            if len(turn_zones) >= 2:
                drone_curr = turn_zones[0]
                drone_neighbors = turn_zones[1:]
                if (target == drone_curr and
                   any(zone in [neigh.name for neigh in target_nighbors]
                       for zone in drone_neighbors)):

                    target_nighbors = list(filter(
                        lambda x: (
                            (x.capacity_usage < x.metadata.max_drones
                             and self.connections[target+'-'+x.name].
                             capacity_usage < self.connections[
                                 target+'-'+x.name].metadata.
                             max_link_capacity) and x.name not in
                            old_zones),
                        self.zones[target].nighbors
                    ))
            # filter old zones
            else:
                target_nighbors = list(filter(
                    lambda x: (x.name not in old_zones),
                    self.zones[target].nighbors
                ))

            for zone in target_nighbors:
                new_cost = zone.cost + distances[target].cost
                if new_cost < distances[zone.name].cost:
                    distances[zone.name].cost = new_cost
                    distances[zone.name].previous_node = target
        return distances

    def construct_path_in_distances(
            self, start: str, target: str,
            distance: Dict[str, 'Graph.NodeInfo']) -> List[str]:
        """
        Reconstructs the path from the result of a pathfinding search.

        Args:
            start: The starting zone name.
            target: The target zone name.
            distance: The distances dictionary from the pathfinding
                      algorithm.

        Returns:
            A list of zone names representing the path.
        """
        if not distance:
            return []
        path: List[str] = []
        while distance[target].previous_node != start:
            if not distance[target].previous_node:
                return []
            path.append(target)
            target = distance[target].previous_node
        path.append(target)
        path.reverse()
        return path

    def resete_zone_and_connec_usage(self) -> None:
        """
        Resets the capacity usage for all zones and connections.

        This is typically called at the beginning of each turn to
        recalculate drone distributions.
        """
        for zone in self.zones:
            self.zones[zone].capacity_usage = \
                len(self.zones[zone].available_drones)

        for connec in self.connections:
            self.connections[connec].capacity_usage = \
                len(self.connections[connec].available_drones)

    def ft_turn(self, drones: deque[Drone], end: Zone) -> List[str]:
        """
        Calculates and executes the moves for all drones in a single turn.

        Args:
            drones: A deque of drones to be moved.
            end: The final destination zone for all drones.

        Returns:
            A list of strings, each representing a drone move command.
        """
        turn: List[str] = []

        for drone in deque(
                filter(lambda x: x.current_zone != end.name, drones)):
            # i will store her the drone current zone and it's neighbors
            turn_zones: List[str] = []
            # her drone in conncection i need move it to it's target zone
            if '-' in drone.current_zone:

                current_zone: Zone = self.zones[drone.current_zone.
                                                split('-', 1)[0]]

                target_zone: Zone = self.zones[drone.current_zone.
                                               split('-', 1)[1]]

                target_drone: Drone = self.connections[drone.current_zone].\
                    available_drones.popleft()

                target_zone.available_drones.append(target_drone)
                turn.append(drone.id+'-'+target_zone.name)
                drone.current_zone = target_zone.name

                self.zones[target_zone.name].capacity_usage += 1

                self.connections[current_zone.name+'-'+target_zone.name]\
                    .capacity_usage += 1

            else:
                turn_zones.append(drone.current_zone)

                current_zone = self.zones[drone.current_zone]

                for zone in current_zone.nighbors:

                    if zone.name not in drone.old_zones and zone.\
                            capacity_usage < zone.metadata.max_drones:
                        turn_zones.append(zone.name)

                distance = self.shortest_path_between_zones(
                    current_zone, end, drone.old_zones, turn_zones)

                drone.old_zones.append(current_zone.name)

                path = self.construct_path_in_distances(
                    current_zone.name, end.name, distance)

                if path and all([zone not in path
                                 for zone in drone.old_zones]):

                    target_zone = self.zones[path[0]]

                    connection_usage = self.connections[
                        current_zone.name+'-'+target_zone.name].capacity_usage

                    connec_capacity = self.connections[
                        current_zone.name+'-'+target_zone.name].metadata.\
                        max_link_capacity

                    if target_zone.capacity_usage < target_zone.metadata.\
                            max_drones and connection_usage < connec_capacity:

                        if target_zone.cost == 2:
                            drone.current_zone = \
                                current_zone.name+'-'+target_zone.name
                            target_drone = \
                                current_zone.available_drones.popleft()
                            self.connections[drone.current_zone].\
                                available_drones.append(target_drone)

                            self.zones[drone.current_zone.split('-')[1]].\
                                capacity_usage += 1
                            self.zones[current_zone.name].\
                                capacity_usage -= 1

                            self.connections[drone.current_zone].\
                                capacity_usage += 1
                            turn.append(drone.id+'-'+drone.current_zone)
                        else:
                            drone.current_zone = target_zone.name
                            target_drone = \
                                current_zone.available_drones.popleft()
                            self.zones[drone.current_zone].\
                                available_drones.append(target_drone)
                            self.zones[drone.current_zone].\
                                capacity_usage += 1
                            self.zones[current_zone.name].\
                                capacity_usage -= 1
                            self.connections[current_zone.name+'-'+drone.
                                             current_zone].capacity_usage += 1

                            turn.append(drone.id+'-'+drone.current_zone)
        self.resete_zone_and_connec_usage()
        return turn

    def simulation(self, end: Zone) -> List[List[str]]:
        """
        Runs the full simulation from start to end.

        It repeatedly calls ft_turn until all drones have reached the
        end zone.

        Args:
            start: The starting zone.
            end: The destination zone.

        Returns:
            A list of lists, where each inner list contains the moves
            for a single turn.
        """
        turns: List[List[str]] = []
        drones: deque[Drone] = self.drones
        while drones:
            turns.append(self.ft_turn(drones, end))
            drones = deque(filter(
                lambda x: x.current_zone != end.name, drones))
        return turns

    def set_drones_capacity_for_start_end_zones(self) -> None:
        """
        Ensures start/end zones can hold all drones if needed.
        """
        for zone in self.zones.values():
            if (zone.name == self.start_end_zones['start_hub'] or
               zone.name == self.start_end_zones['end_hub']):
                if zone.metadata.max_drones < self.nb_drones:
                    zone.metadata.max_drones = self.nb_drones

    def move_all_drones_to_start_zone(self) -> None:
        """
        Places all drones in the starting zone.
        """
        start_zone: Zone = self.zones[
            self.start_end_zones['start_hub']]

        start_zone.available_drones.extend(self.drones)
        start_zone.capacity_usage = len(start_zone.available_drones)
        for drone in start_zone.available_drones:
            drone.current_zone = start_zone.name

    def remove_drones_from_all_zones_connecs(self) -> None:
        """
        Clears all drones from every zone in the graph.
        """
        for zone in self.zones.values():
            zone.available_drones.clear()
            zone.capacity_usage = 0
        for connec in self.connections.values():
            connec.available_drones.clear()
            connec.capacity_usage = 0

    def check_start_and_end_zone_not_blocked(self) -> None:
        """
        Verifies that the start and end zones are not of type 'blocked'.
        """
        for zone in self.zones:
            if zone in self.start_end_zones.values():
                if self.zones[zone].metadata.zone_type == \
                        ZoneTypes('blocked'):
                    line_nb = self.zones[zone].metadata.line_number
                    raise ValueError('at line '
                                     f"{line_nb}: "
                                     f'zone "{self.zones[zone].name}" '
                                     'can\'t be of type blocked')

    def __str__(self) -> str:
        return str(
            f'number of drones      : {self.nb_drones}\n'
            f'number of  zones      : {len(self.zones)}\n'
            f'number of connections : {len(self.connections)}\n'
            f'available drones      : {self.drones}\n'
            f'available zones       : {self.zones}\n'
            f'available connections : {self.connections}\n'
            f'start & end zones     : {self.start_end_zones}'
        )

    def __repr__(self) -> str:
        return self.__str__()


if __name__ == '__main__':
    if len(argv) == 3 or len(argv) == 2:
        flag: str | None = argv[2] if len(argv) == 3 else None
        if flag and flag != '--visual':
            print('Error invalid syntax try:\n'
                  'python main.py map_file_example.txt\nor:\n'
                  'python main.py map_file_example.txt --visual')
            exit(1)

        file: str = argv[1]
        if not file.endswith('.txt'):
            print('Error invalid syntax try:\n'
                  'python main.py map_file_example.txt\nor:\n'
                  'python main.py map_file_example.txt --visual')
            exit(0)
        try:
            p = Parser(file)
            p.parse_map()
            graph = Graph(p.nb_drones, p.zones, p.connections,
                          p.start_end_zones_name)
            graph.check_start_and_end_zone_not_blocked()
            graph.set_drones_capacity_for_start_end_zones()
            graph.move_all_drones_to_start_zone()
            # start_zone: Zone = graph.zones[
            #     graph.start_end_zones['start_hub']]

            end_zone: Zone = graph.zones[
                graph.start_end_zones['end_hub']]
            graph.find_nighbors_for_every_zone()

            if not flag:
                turns: List[List[str]] = graph.simulation(end_zone)
                for turn in turns:
                    print(' '.join(turn))
            else:

                from visualizer import Visualizer
                vis = Visualizer(graph)
                vis.run_gui()
        except Exception as e:
            print(e.__class__.__name__, e)
            exit(1)
    else:
        print('Error invalid syntax try:\n'
              'python main.py map_file_example.txt\nor:\n'
              'python main.py map_file_example.txt --visual')
