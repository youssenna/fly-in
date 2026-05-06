from typing import Any
import pygame
from parser import Zone, Connection, ZoneTypes
from time import sleep
from random import choice
from collections import deque
from parser import Drone


class Visualizer:
    from main import Graph
   
    def __init__(self, graph: Graph):
        self.graph = graph
        pygame.init()
        pygame.font.init()
        self.font1: Any = pygame.font.SysFont('file', 15)
        self.font2: Any = pygame.font.SysFont('file', 13)
        self.font3: Any = pygame.font.SysFont('file', 40)

    def draw_zone(self, zone: Zone, surface: Any):
        try:
            # pygame.draw.rect(surface, zone.metadata.color,
            #                  (zone.x * 80 + self.screen_w / 7 - 100,
            #                   zone.y * 150 + self.screen_h / 2,
            #                   60, 60), 0, 3)
            pygame.draw.circle(surface, zone.metadata.color,
                             (zone.x * 80 + self.screen_w / 7 - 70,
                              zone.y * 150 + self.screen_h / 2 + 30), 35, 0)
        except ValueError:
            colors = {
                'normal': 'blue',
                'blocked': 'black',
                'restricted': 'purple',
                'priority': 'cyan'
            }
            if (zone.name == self.graph.start_end_zones.get('start_hub') or
               zone.name == self.graph.start_end_zones.get('end_hub')):
                color: str = 'green'
            elif not zone.nighbors:
                color = 'red'
            else:
                color = colors.get(zone.metadata.zone_type.value)
            # pygame.draw.rect(surface, color,
            #                  (zone.x * 80 + self.screen_w / 7 - 100,
            #                   zone.y * 150 + self.screen_h / 2,
            #                   60, 60), 0, 3)

            pygame.draw.circle(surface, color,
                             (zone.x * 80 + self.screen_w / 7 - 70,
                              zone.y * 150 + self.screen_h / 2 + 30), 35, 0)
            
        self.draw_drones(zone, surface)
        # pygame.draw.rect(surface, 'white',
        #                  (zone.x * 80 + self.screen_w / 7 - 100,
        #                   zone.y * 150 + self.screen_h / 2,
        #                   60, 60), 3, 3)
        pygame.draw.circle(surface, 'white',
                             (zone.x * 80 + self.screen_w / 7 - 70,
                              zone.y * 150 + self.screen_h / 2 + 30), 35, 3)
        zone_name = self.font2.render(f'{zone.name}', True, 'green')
        available_d = self.font2.render(
            'drones: '
            f'{len(zone.available_drones)}',
            True, 'white')
        capacity_d = self.font2.render(
            f'CAPACITY: {zone.metadata.max_drones}', True, 'white')
        cost = self.font2.render(
            f'COST: {zone.cost}', True, 'white')
        surface.blit(zone_name, (zone.x * 80 + self.screen_w / 7 - 100,
                     zone.y * 150 + self.screen_h / 2 + 70))
        surface.blit(available_d, (zone.x * 80 + self.screen_w / 7 - 100,
                     zone.y * 150 + self.screen_h / 2 + 80))
        surface.blit(capacity_d, (zone.x * 80 + self.screen_w / 7 - 100,
                     zone.y * 150 + self.screen_h / 2 + 90))
        surface.blit(cost, (zone.x * 80 + self.screen_w / 7 - 100,
                     zone.y * 150 + self.screen_h / 2 + 100))
            
    def draw_drones(self, zone: Zone, surface: Any):
        imgs = [pygame.image.load('./drone_picture3.png')
                for _ in range(len(zone.available_drones))
                ]
        color = choice(['red', 'yellow', 'orange', 'white'])
        for img in imgs:
            surface.blit(img, (zone.x * 80 + self.screen_w / 7 - 100,
                         zone.y * 150 + self.screen_h / 2))

            drone_info = self.font2.render(
                f'{[drone.id for drone in zone.available_drones]}',
                True, color)
            surface.blit(drone_info, (zone.x * 80 + self.screen_w / 7 - 100,
                         zone.y * 150 + self.screen_h / 2 - 10))

    def connec_zones(self, connec: Connection, surface: Any):
        pygame.draw.line(surface, (0, 56, 54), 
                         (connec.zone1.x * 80 + self.screen_w / 7 + 25 - 100,
                          connec.zone1.y * 150 + self.screen_h / 2 + 25),
                         (connec.zone2.x * 80 + self.screen_w / 7 + 25 - 100,
                          connec.zone2.y * 150 + self.screen_h / 2 + 25),
                         5)
        # if drones_len := len(self.graph.connections.get(connec.zone1.name+'-'+connec.zone2.name).available_drones):
        #     imgs = [pygame.image.load('./drone_picture3.png')
        #             for _ in range(drones_len)
        #             ]
            
        #     for img in imgs:
        #         surface.blit(img, (connec.zone2.x * 80 + self.screen_w / 7 - 90,
        #                     connec.zone2.y * 150 + self.screen_h / 2 - 10))

        #         drone_info = self.font2.render(
        #             f'{[drone.id for drone in self.graph.connections.get(connec.zone1.name+'-'+connec.zone2.name).available_drones]}',
        #             True, 'white')
        #         surface.blit(drone_info, (connec.zone2.x * 80 + self.screen_w / 7 - 90,
        #                     connec.zone2.y * 150 + self.screen_h / 2 - 20))
            


    def run_gui(self):
        info: Any = pygame.display.Info()
        self.screen_w, self.screen_h = info.current_w, info.current_h
        screen: Any = pygame.display.set_mode((self.screen_w, self.screen_h),
                                              pygame.RESIZABLE)
        pygame.display.set_caption('❣️❣️❣️ yousenna FLY-IN project ❣️❣️❣️')
        run: bool = True
        self.graph.remove_drones_from_all_zones()
        self.graph.move_all_drones_to_start_zone()
        nb_turnes = 0
        end_zone_name: str = self.graph.start_end_zones.get('end_hub')
        start_zone_name: str = self.graph.start_end_zones.get('start_hub')
        drones: deque[Drone] = deque(self.graph.drones)
        
        while run:
            
            screen.fill((11, 0, 89))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
            
            keys = pygame.key.get_pressed()

            if keys[pygame.K_SPACE]:
                sleep(0.2)
                if (len(self.graph.zones.get(end_zone_name).available_drones)
                   != self.graph.nb_drones):
                    nb_turnes += 1
                    self.graph.ft_turn(drones, self.graph.zones.get(end_zone_name))
            if keys[pygame.K_TAB]:
                self.screen_w *= 0.9
                # self.screen_h *= 0.5
            if keys[pygame.K_DOWN]:
                self.graph.remove_drones_from_all_zones()
                self.graph.move_all_drones_to_start_zone()
                drones: deque[Drone] = deque(self.graph.drones)
                for drone in drones:
                    drone.current_zone = start_zone_name
                    drone.old_zones.clear()
                nb_turnes = 0
            turns_counter = self.font3.render(f'Turnes: {nb_turnes}', True,
                                              'white')
            
            nb_drones = self.font3.render('number of drones: '
                                          f'{self.graph.nb_drones}',
                                          True, 'white')
            
            screen.blit(turns_counter, (10, 10))
            screen.blit(nb_drones, (10, 40))
            for connec in self.graph.connections.values():
                self.connec_zones(connec, screen)

            for zone in self.graph.zones.values():
                self.draw_zone(zone, screen)

            pygame.display.update()
            sleep(0.1)

        pygame.QUIT
