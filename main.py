# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  main.py                                           :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: yousenna <yousenna@student.42.fr>         +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/03/30 16:47:56 by yousenna        #+#    #+#               #
#  Updated: 2026/04/04 17:04:47 by yousenna        ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

from typing import Dict, List, Optional, Tuple, Union, Any
from parser import Parser, Zone, Connection, ZoneTypes
from sys import argv, exit
import tkinter


class Drone:
    def __init__(self, id: str):
        self.id = id


class Graph:
    def __init__(self, nb_drones: int, zones: Dict[str, Zone],
                 connections: List[Connection],
                 start_end_zones: Dict[str, str]):
        self.nb_drones: int = nb_drones
        self.connections: List[Connection] = connections
        # after all zones valid with parser file for every zone i will
        # find it's nighbors
        self.zones: Dict[str, Zone] = zones
        self.start_end_zones: Dict[str, str] = start_end_zones
        self.drones: List[Drone] = self._creat_drones(nb_drones)
        self.paths: List[List[Zone]] = []
        self.path: List[Zone] = []

    def _find_nighbors_for_every_zone(self, zone_name: str) -> None:
        return [
            connec.zone2 for connec in self.connections
            if connec.zone1.name == zone_name
        ]

    def _creat_drones(self, nb_drones: int) -> List[Drone]:
        return [Drone('D' + str(n+1)) for n in range(nb_drones)]

    def paths_finding(self, start: Zone, end: Zone, path: List[Zone] = []) -> None:
        start.nighbors = self._find_nighbors_for_every_zone(start.name)
        if start not in self.path:
            self.path.append(start)
        else:
            return
        if (not start.nighbors or
           start.metadata.zone_type == ZoneTypes('blocked')):
            return
        if start.name == end.name:
            self.paths.append(path)
            return

        for zone in start.nighbors:
            # if zone not in path:
            self.paths_finding(zone, end, path)
            path.remove(zone)

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
        # print(graph.zones.get('start').nighbors)
        # print(graph.start_end_zones)
        # print(graph.zones)
        start_zone = graph.zones.get(
            graph.start_end_zones.get('start_hub'))
        end_zone = graph.zones.get(
            graph.start_end_zones.get('end_hub'))
        graph.paths_finding(graph.zones.get('start'), end_zone)
        # print(start_zone.nighbors)
        # print(end_zone)
        print(graph.paths)
        for path in graph.paths:
            print(path)
        # print(start_zone.nighbors)
        # except Exception as e:
        #     print(e.__class__.__name__, e)
            # exit(1)
    else:
        print('Error invalid syntax try:\n'
              'python main.py map_file_example.txt\nor:\n'
              'python main.py map_file_example.txt --visual')
        
        # print(graph.file_name)
    
    # print(flag)
        
    # print(file)
            
    # print(len(argv))