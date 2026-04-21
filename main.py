# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  main.py                                           :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: yousenna <yousenna@student.42.fr>         +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/03/30 16:47:56 by yousenna        #+#    #+#               #
#  Updated: 2026/04/21 19:13:02 by yousenna        ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

from typing import Dict, List, Optional, Tuple, Union, Any
from parser import Parser, Zone, Connection, ZoneTypes, Drone
from sys import argv, exit
from collections import deque
from math import inf
import pygame


class Graph:
    def __init__(self, nb_drones: int, zones: Dict[str, Zone],
                 connections: List[Connection],
                 start_end_zones: Dict[str, str]):
        self.nb_drones: int = nb_drones
        self.connections: Dict[str, Connection] = {
            con.zone1.name+'-'+con.zone2.name: con for con in connections
        }
        # after all zones valid with parser file for every zone i will
        # find it's nighbors
        self.zones: Dict[str, Zone] = zones
        self.start_end_zones: Dict[str, str] = start_end_zones
        self.drones: List[Drone] = self._creat_drones(nb_drones)
        self.paths: List[List[Zone]] = []
        self.path: List[Zone] = []

    def _find_nighbors(self, zone_name: str) -> List[Zone]:
        return [
            self.connections.get(connec).zone2 for connec in self.connections
            if self.connections.get(connec).zone1.name == zone_name
        ]
    
    def find_nighbors_for_every_zone(self):
        for zone in self.zones.values():
            zone.nighbors.extend(self._find_nighbors(zone.name))

    def _creat_drones(self, nb_drones: int) -> deque[Drone]:
        return deque(Drone('D' + str(n+1)) for n in range(nb_drones))

    class NodeInfo:
        def __init__(self, cost: Union[float, int], previous_node: str):
            self.cost: Union[float, int] = cost
            self.previous_node: str = previous_node
        
        def __str__(self) -> str:
            return f'cost = {self.cost} | previous node = {self.previous_node}'
        
        def __repr__(self) -> str:
            return self.__str__()
        
    def find_shortest_path_with_dijikstra(self, start: Zone, end: Zone
                                          ) -> List[str]:
        if start.name == end.name:
            return []
        visited_zones: deque[str] = deque()
        unvisited_zones: deque[str] = deque(self.zones.keys())
        info: Dict[str, Graph.NodeInfo] = {
            zone: self.NodeInfo(inf, '') for zone in unvisited_zones
        }
        info.get(start.name).cost = 0
        path: List[str] = []
        
        def find_path_between_two_zone_in_info(target: str) -> List[str]:
            path: List[str] = []
            # previous_nodes: List[str] = [zone_name for zone_name in info.get]
            while info.get(target).previous_node != start.name:
                path.append(target)
                target = info.get(target).previous_node
            path.append(target)
            path.reverse()
            # print(info)
            return path
            
        while unvisited_zones:
            unvisited_zones = deque(sorted(
                unvisited_zones,
                key=lambda x: (info.get(x).cost,
                               self.zones.get(x).perfect)))
            target: str = unvisited_zones.popleft()
            target_nighbors: List[Zone] = list(filter(
                lambda x: x.cost is not inf,
                self.zones.get(target).nighbors))
            # target_nighbors = list(sorted(
            #     target_nighbors,
            #     key=lambda x: (self.zones.get(x.name).cost,
            #                    self.zones.get(x.name).perfect))
            # )
            # if target == 'bottleneck':
            #     print(target_nighbors)
            for zone in target_nighbors:
                new_cost: int = zone.cost + info.get(target).cost
                if new_cost < info.get(zone.name).cost:
                    info.get(zone.name).cost = new_cost
                    info.get(zone.name).previous_node = target
                # elif new_cost == info.get(zone.name).cost:
                #     target_nighbor_prev__name: str = \
                #         info.get(zone.name).previous_node
                #     sort = sorted([target_nighbor_prev__name, target],
                #                   key=lambda x: self.zones.get(x).perfect)
                #     info.get(zone.name).previous_node = sort[0]
                    
            visited_zones.append(target)
        # print(info)
        if info.get(end.name).cost != inf:
            path = find_path_between_two_zone_in_info(end.name)
        return path[:]
        
    def sort_zones_from_start_to_end(self, end: str) -> List[str]:
        zones_: List[Tuple[str, int]] = [
            (zone_name,
             len(self.find_shortest_path_with_dijikstra(
                 self.zones.get(zone_name),
                 self.zones.get(end))))
            for zone_name in self.zones
        ]
        zones_ = sorted(zones_, key=lambda x: x[1], reverse=False)
        return [x[0] for x in zones_]
        
        
    def ft_turn(self, end: str) -> List[str]:
        # zones_name: List[str] = list(self.zones.keys())
        zones_name: List[str] = self.sort_zones_from_start_to_end(end)
        # zones_name.reverse()
        # print('fuck', zones_name)
        # return
        # print('fuck you', zones_name)
        turn: List[str] = []
        for zone in zones_name:
            if self.zones.get(zone).available_drones and zone != end:
                path: List[str] = self.find_shortest_path_with_dijikstra(
                    self.zones.get(zone), self.zones.get(end))
                
                # print(path)
                # if path:
                target_zone = path[0]
                # else:
                #     continue
                target_zone_capacity: int = \
                    self.zones.get(target_zone).metadata.max_drones
                
                target_connec_capacity: int = \
                    self.connections.get(zone+'-'+target_zone).\
                    metadata.max_link_capacity
                
                current_drones: int = len(
                    self.zones.get(target_zone).available_drones)
                
                drones_to_move = target_zone_capacity - current_drones
                
                restrected_drones: List[Drone] = []
                for _ in range(min([drones_to_move, target_connec_capacity])):
                    if self.zones.get(zone).available_drones:
                        target_drone = \
                            self.zones.get(zone).available_drones.popleft()
                        if (self.zones.get(target_zone)
                           .metadata.zone_type == ZoneTypes('restricted')
                           and not target_drone.restrected_target_zone):

                            target_drone.restrected_target_zone = True
                            restrected_drones.append(target_drone)
                            turn.append(f'{target_drone.id}-{zone}'
                                        f'-{target_zone}')
                            continue
                        
                        if target_drone.restrected_target_zone:
                            target_drone.restrected_target_zone = False

                        self.zones.get(target_zone)\
                            .available_drones.append(target_drone)
                        turn.append(f'{target_drone.id}-{target_zone}')
                for drone in restrected_drones:
                    self.zones.get(zone).available_drones.appendleft(drone)
        # print(turn)
                # print(self.zones.get(zone).available_drones)
                # break
            # if 
            # if path := self.find_shortest_path_with_dijikstra(
            #     self.zones.get(zone), self.zones.get(end)):
            #     print(path[0])
                
        # for zone in self.zones.keys().__reversed__():
        return turn

    def simulation(self, start: Zone, end: Zone) -> List[List[str]]:
        turns: List[List[str]] = []
        while len(end.available_drones) != self.nb_drones:
            turns.append(self.ft_turn(end.name))
            # print(self.drones)
            # break
            # break
        return turns
        # for turn in turns:
            # print(turn)

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
        # print(start_zone.available_drones)
        for drone in start_zone.available_drones:
            drone.current_zone = start_zone.name

    def remove_drones_fron_all_zones(self) -> None:
        for zone in self.zones.values():
            zone.available_drones = deque()
        
    
    # def simulation_output(self, start: Zone):
    #     start.available_drones.extend(self.drones)
    #     while len(self.path[x].available_drones) != self.nb_drones:
    #         x: int = len(self.path) - 1
    #         while x >= 0:
    #             if x > 0:
    #                 if self.path[x-1].available_drones:
                        
        

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
        graph.set_drones_capacity_for_start_end_zones()
        graph.move_all_drones_to_start_zone()
        # print(graph.zones.get('start').nighbors)
        # prhint(graph.start_end_zones)
        # print(graph.zones)
        start_zone: Zone = graph.zones.get(
            graph.start_end_zones.get('start_hub'))
        
        end_zone: Zone = graph.zones.get(
            graph.start_end_zones.get('end_hub'))
        graph.find_nighbors_for_every_zone()
        # print(start_zone.nighbors)
        graph.turns = graph.simulation(start_zone, end_zone)
        if not flag:
            for turn in graph.turns:
                print(turn)
        else:
            
            from visualizer import Visualizer
            vis = Visualizer(graph)
            vis.run_gui()
            # pygame.init()
            # info = pygame.display.Info()
            # screen_width = info.current_w
            # screen_height = info.current_h
            # screen = pygame.display.set_mode((screen_width, screen_height),
            #                                  pygame.RESIZABLE)
            # pygame.display.set_caption('yousenna FLY-IN ')
            # run = True
            # while run:
            #     screen.fill('red')
            #     # 1. Check for events (clicks, keys, etc.)
            #     for event in pygame.event.get():
            #         if event.type == pygame.QUIT:
            #             run = False
                    
            #     pygame.draw.circle(screen, 'blue', (screen_width / 50, screen_width / 50),
            #                        screen_width / 50, 5)
            #     pygame.display.update()
            #     from time import sleep
            #     sleep(0.2)
            #     # screen.fill('blue')
            #     pygame.draw.rect(screen, 'green', (screen_width / 50,
            #                                         screen_width / 50,
            #                                         screen_width / 50,
            #                                         screen_width / 50), 0, 5)
            #     pygame.draw.rect(screen, 'yellow', (screen_width / 50,
            #                                         screen_width / 50,
            #                                         screen_width / 50,
            #                                         screen_width / 50), 5, 5)
            #     pygame.draw.rect(screen, 'green', (120, 120, 120, 200), 10)
            #     pygame.draw.line(screen, 'black', ((screen_width / 50) * 2,
            #                                        (screen_width / 50) * 2),
            #                                       (120, 120), 5)
            #     pygame.display.flip()
                
            #     sleep(0.2)
            
            # exit = False
            
        
        # path = graph.find_shortest_path_with_dijikstra(start_zone, end_zone)
        # print(path)
        # print(graph.path)
        # print(start_zone.nighbors)
        # print(end_zone)
    # except Exception as e:
    #         print(e.__class__.__name__, e)
    #         exit(1)
    else:
        print('Error invalid syntax try:\n'
              'python main.py map_file_example.txt\nor:\n'
              'python main.py map_file_example.txt --visual')
        
        # print(graph.file_name)
    
    # print(flag)
        
    # print(file)
            
    # print(len(argv))