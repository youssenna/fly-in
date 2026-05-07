# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  main.py                                           :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: yousenna <yousenna@student.42.fr>         +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/03/30 16:47:56 by yousenna        #+#    #+#               #
#  Updated: 2026/05/07 15:12:10 by yousenna        ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

from typing import Dict, List, Tuple, Union
from parser import Parser, Zone, Connection, ZoneTypes, Drone
from sys import argv, exit
from collections import deque
from math import inf


class Graph:
    def __init__(self, nb_drones: int, zones: Dict[str, Zone],
                 connections: List[Connection],
                 start_end_zones: Dict[str, str]):
        self.nb_drones: int = nb_drones
        self.connections: Dict[str, Connection] = {
            con.zone1.name+'-'+con.zone2.name: con for con in connections
        }
        self.zones: Dict[str, Zone] = zones
        self.start_end_zones: Dict[str, str] = start_end_zones
        self.drones: List[Drone] = self._creat_drones(nb_drones)
        self.paths: List[List[Zone]] = []
        self.path: List[Zone] = []
        self.distance: Dict[List[str], Graph.NodeInfo] = {}

    def _find_nighbors(self, zone_name: str) -> List[Zone]:
        return [
            self.connections.get(connec).zone2 for connec in self.connections
            if self.connections.get(connec).zone1.name == zone_name
        ]

    def find_nighbors_for_every_zone(self):
        for zone in self.zones.values():
            zone.nighbors.extend(self._find_nighbors(zone.name))

    @staticmethod
    def _creat_drones(nb_drones: int) -> deque[Drone]:
        return deque(Drone('D' + str(n+1)) for n in range(nb_drones))

    class NodeInfo:
        def __init__(self, cost: Union[float, int], previous_node: str):
            self.cost: Union[float, int] = cost
            self.previous_node: str = previous_node

        def __str__(self) -> str:
            return f'cost = {self.cost} | previous node = {self.previous_node}'

        def __repr__(self) -> str:
            return self.__str__()

    def shortest_path_between_zones(
            self, start: Zone, end: Zone,
            old_zones: List[str], turn_zones: List[str]
            ) -> Tuple[List[str], Dict[str, NodeInfo]]:

        if start.name == end.name:
            return []
        visited_zones: deque[str] = deque()
        unvisited_zones: deque[str] = deque(self.zones.keys())
        distances: Dict[str, Graph.NodeInfo] = {
            zone: self.NodeInfo(inf, '') for zone in unvisited_zones
        }
        distances.get(start.name).cost = 0

        while unvisited_zones:
            unvisited_zones = deque(sorted(
                unvisited_zones,
                key=lambda x: (distances.get(x).cost,
                               self.zones.get(x).perfect)))
            target: str = unvisited_zones.popleft()
            # filter blocked_zones
            target_nighbors: List[Zone] = list(filter(
                lambda x: x.cost is not inf, self.zones.get(target).nighbors))

            # filter full zones and connection and old zones
            if len(turn_zones) >= 2:
                drone_curr = turn_zones[0]
                drone_neighbors = turn_zones[1:]
                if (target == drone_curr and
                   any(zone in [neigh.name for neigh in target_nighbors]
                       for zone in drone_neighbors)):

                    target_nighbors: List[Zone] = list(filter(
                        lambda x: ((x.capacity_usage < x.metadata.max_drones
                                    and self.connections.
                                    get(target+'-'+x.name).
                                    capacity_usage < self.connections.
                                    get(target+'-'+x.name).metadata.
                                    max_link_capacity) and x.name not in
                                   old_zones), self.zones.get(target).nighbors
                            )
                    )       
            # filter old zones
            else:
                target_nighbors: List[Zone] = list(filter(
                    lambda x: (x.name not in old_zones),
                    self.zones.get(target).nighbors
                    )
                )
            
            for zone in target_nighbors:
                new_cost: int = zone.cost + distances.get(target).cost
                if new_cost < distances.get(zone.name).cost:
                    distances.get(zone.name).cost = new_cost
                    distances.get(zone.name).previous_node = target
            visited_zones.append(target)
        return distances
    
    
    def construct_path_in_distances(
            self, start: str, target: str, distance) -> List[str]:
        path: List[str] = []
        while distance.get(target).previous_node != start:
            if not distance.get(target).previous_node:
                return []
            path.append(target)
            target = distance.get(target).previous_node
        path.append(target)
        path.reverse()
        return path

    def resete_zone_and_connec_usage(self) -> None:
        for zone in self.zones:
            self.zones.get(zone).capacity_usage = len(self.zones.get(zone).available_drones)
        
        for connec in self.connections:
            self.connections.get(connec).capacity_usage = len(self.connections.get(connec).available_drones)

    def ft_turn(self, drones: deque[Drone], end: Zone) -> List[str]:
        turn: List[str] = []
        
        
        self.resete_zone_and_connec_usage()
        for drone in deque(filter(lambda x: x.current_zone != end.name, drones)):
            # i will store her the drone current zone and it's neighbors
            turn_zones: List[str] = []
            # her drone in conncection i need move it to it's target zone
            if '-' in drone.current_zone:
                current_zone: Zone = self.zones.get(drone.current_zone.split('-', 1)[0])
                target_zone: Zone = self.zones.get(drone.current_zone.split('-', 1)[1])
                target_drone: Drone = self.connections.get(drone.current_zone).available_drones.popleft()
                target_zone.available_drones.append(target_drone)
                turn.append(drone.id+'-'+target_zone.name)
                drone.current_zone = target_zone.name
                
                self.zones.get(target_zone.name).capacity_usage += 1
                self.connections.get(current_zone.name+'-'+target_zone.name).capacity_usage += 1

            else:
                turn_zones.append(drone.current_zone)
                
                current_zone: Zone = self.zones.get(drone.current_zone)

                for zone in current_zone.nighbors:
                    if zone.name not in drone.old_zones and zone.capacity_usage < zone.metadata.max_drones:
                        turn_zones.append(zone.name)

                distance = self.shortest_path_between_zones(current_zone, end, drone.old_zones, turn_zones)
                drone.old_zones.append(current_zone.name)
                path = self.construct_path_in_distances(current_zone.name, end.name, distance)
                
                if path and all([zone not in path for zone in drone.old_zones]):
                    target_zone: Zone = self.zones.get(path[0])
                    
                    connection_usage = self.connections.get(
                        current_zone.name+'-'+target_zone.name).capacity_usage
                    
                    connec_capacity = self.connections.get(
                        current_zone.name+'-'+target_zone.name)\
                            .metadata.max_link_capacity
                    
                    if (target_zone.capacity_usage < target_zone.metadata.max_drones
                       and connection_usage < connec_capacity):
                        if target_zone.cost == 2:
                            drone.current_zone = current_zone.name+'-'+target_zone.name
                            target_drone = current_zone.available_drones.popleft()
                            self.connections.get(drone.current_zone).available_drones.append(target_drone)
                            
                            
                            self.zones.get(drone.current_zone.split('-')[1]).capacity_usage += 1
                            self.zones.get(current_zone.name).capacity_usage -= 1
                            
                            self.connections.get(drone.current_zone).capacity_usage += 1
                            turn.append(drone.id+'-'+drone.current_zone)
                        else:
                            drone.current_zone = target_zone.name
                            target_drone = current_zone.available_drones.popleft()
                            self.zones.get(drone.current_zone).available_drones.append(target_drone)
                            self.zones.get(drone.current_zone).capacity_usage += 1
                            self.zones.get(current_zone.name).capacity_usage -= 1
                            self.connections.get(current_zone.name+'-'+drone.current_zone).capacity_usage += 1
                            
                            
                            turn.append(drone.id+'-'+drone.current_zone)
        # print(turn)
        return turn

    def simulation(self, start: Zone, end: Zone) -> List[List[str]]:
        turns: List[List[str]] = []
        drones: deque[Drone] = deque(self.drones)
        while drones:
            turns.append(self.ft_turn(drones, end))
            drones = list(filter(lambda x: x.current_zone != end.name, drones))
        return turns

        
    def set_drones_capacity_for_start_end_zones(self) -> None:
        for zone in self.zones.values():
            if (zone.name == self.start_end_zones.get('start_hub') or
               zone.name == self.start_end_zones.get('end_hub')):
                if zone.metadata.max_drones < self.nb_drones:
                    zone.metadata.max_drones = self.nb_drones
    
    def move_all_drones_to_start_zone(self) -> None:
        start_zone: Zone = self.zones.get(
            self.start_end_zones.get('start_hub')
        )
        start_zone.available_drones.extend(self.drones)
        start_zone.capacity_usage = len(start_zone.available_drones)
        for drone in start_zone.available_drones:
            drone.current_zone = start_zone.name

    def remove_drones_from_all_zones(self) -> None:
        for zone in self.zones.values():
            zone.available_drones.clear()
            zone.capacity_usage = 0
    
    def check_start_and_end_zone_not_blocked(self):
        for zone in self.zones:
            if zone in self.start_end_zones.values():
                if self.zones.get(zone).metadata.zone_type == ZoneTypes('blocked'):
                    raise ValueError(f'at line {self.zones.get(zone).\
                                                metadata.line_number}: '
                                    f'zone "{self.zones.get(zone).name}" '
                                    'can\'t be of type blocked [start or end '
                                    'zone]')

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
    if len(argv) == 1:
        print('Error you must add map file excepted command:\n'
              'python main.py map_file_example.txt\n'
              'or Use the --visual flag to see colored terminal output during '
              'simulation!:\n'
              'python main.py map_file_example.txt --visual')
        exit(1)
    if len(argv) == 3 or len(argv) == 2:
        flag: bool = True if '--visual' in argv[1:] else False
        if flag and len(argv) == 2:
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
        # try:
        p = Parser(file)
        p.parse_map()
        graph = Graph(p.nb_drones, p.zones, p.connections,
                    p.start_end_zones_name)
        graph.check_start_and_end_zone_not_blocked()
        graph.set_drones_capacity_for_start_end_zones()
        graph.move_all_drones_to_start_zone()
        start_zone: Zone = graph.zones.get(
            graph.start_end_zones.get('start_hub'))
        
        end_zone: Zone = graph.zones.get(
            graph.start_end_zones.get('end_hub'))
        graph.find_nighbors_for_every_zone()
        
        if not flag:
            graph.turns = graph.simulation(start_zone, end_zone)
            for turn in graph.turns:
                print(' '.join(turn))
                # print(turn)
        else:
            
            from visualizer import Visualizer
            vis = Visualizer(graph)
            vis.run_gui()
            
        # except Exception as e:
        #     print(e.__class__.__name__, e)
        #     exit(1)
    else:
        print('Error invalid syntax try:\n'
              'python main.py map_file_example.txt\nor:\n'
              'python main.py map_file_example.txt --visual')
