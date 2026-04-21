from typing import Any
import pygame
from parser import Zone, Connection
from time import sleep
from random import choice


class Visualizer:
    from main import Graph
   
    def __init__(self, graph: Graph):
        self.graph = graph
        pygame.init()
        pygame.font.init()
        self.font1: Any = pygame.font.SysFont('file', 15)
        self.font2: Any = pygame.font.SysFont('file', 12)
        self.font3: Any = pygame.font.SysFont('file', 40)

    def draw_zone(self, zone: Zone, surface: Any):
        pygame.draw.rect(surface, zone.metadata.color,
                         (zone.x * 80 + self.screen_w / 7 - 100,
                          zone.y * 150 + self.screen_h / 2,
                          60, 60), 0, 3)
        self.draw_drones(zone, surface)
        pygame.draw.rect(surface, 'white',
                         (zone.x * 80 + self.screen_w / 7 - 100,
                          zone.y * 150 + self.screen_h / 2,
                          60, 60), 3, 3)
        if len(zone.name) > 6:
            text = self.font2.render(f'{zone.name}', True, 'green')
            text1 = self.font2.render(f'drones: {len(zone.available_drones)}',
                                      True, 'white')
            surface.blit(text, (zone.x * 80 + self.screen_w / 7 - 100,
                                zone.y * 150 + self.screen_h / 2 + 70))
            surface.blit(text1, (zone.x * 80 + self.screen_w / 7 - 100,
                                 zone.y * 150 + self.screen_h / 2 + 80))
        else:
            text = self.font1.render(f'{zone.name}', True, 'green')
            surface.blit(text, (zone.x * 80 + self.screen_w / 7 - 100,
                                zone.y * 150 + self.screen_h / 2 + 70))
            text1 = self.font1.render(f'drones: {len(zone.available_drones)}',
                                      True, 'white')
            surface.blit(text1, (zone.x * 80 + self.screen_w / 7 - 100,
                                 zone.y * 150 + self.screen_h / 2 + 80))
            
            
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
        

    def run_gui(self):
        info: Any = pygame.display.Info()
        self.screen_w, self.screen_h = info.current_w, info.current_h
        screen: Any = pygame.display.set_mode((self.screen_w, self.screen_h),
                                              pygame.RESIZABLE)
        pygame.display.set_caption('❣️❣️❣️ yousenna FLY-IN project ❣️❣️❣️')
        run: bool = True
        self.graph.remove_drones_fron_all_zones()
        self.graph.move_all_drones_to_start_zone()
        nb_turnes = 0
        end_zone_name: str = self.graph.start_end_zones.get('end_hub')
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
                    self.graph.ft_turn(end_zone_name)
            

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