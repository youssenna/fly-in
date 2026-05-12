# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  visualizer.py                                     :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: yousenna <yousenna@student.42.fr>         +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/05/07 16:44:41 by yousenna        #+#    #+#               #
#  Updated: 2026/05/12 20:26:07 by yousenna        ###   ########.fr        #
#                                                                           #
# ************************************************************************* #
from typing import Any, Dict
import pygame
from parser import Zone, Connection, Drone
from time import sleep
from random import choice
from collections import deque


class Visualizer:
    """
    Handles the graphical visualization of the simulation using Pygame.
    """
    from main import Graph

    def __init__(self, graph: Graph):
        self.graph = graph
        self.offset_x: int = 0
        self.offset_y: int = 0
        self.drone_img: Any = pygame.image.load('./drone_picture3.png')
        pygame.init()
        pygame.font.init()
        self.font1: Any = pygame.font.SysFont('file', 15)
        self.font2: Any = pygame.font.SysFont('file', 13)
        self.font3: Any = pygame.font.SysFont('file', 40)

    def draw_zone(self, zone: Zone, surface: Any) -> None:
        """
        Draws a single zone on the Pygame surface.

        Args:
            zone: The Zone object to draw.
            surface: The Pygame surface to draw on.
        """
        try:
            pygame.draw.circle(surface, zone.metadata.color,
                               (zone.x * 80 + self.screen_w / 2 - 70 +
                                self.offset_x,
                                zone.y * 150 + self.screen_h / 2 + 30 +
                                self.offset_y),
                               35, 0)
        except Exception:
            colors: Dict[str, str] = {
                'normal': 'blue',
                'blocked': 'black',
                'restricted': 'purple',
                'priority': 'cyan'
            }
            if (zone.name == self.graph.start_end_zones.get('start_hub') or
               zone.name == self.graph.start_end_zones.get('end_hub')):
                color: Any = 'green'
            elif not zone.nighbors:
                color = 'red'
            else:
                color = colors.get(zone.metadata.zone_type.value)

            pygame.draw.circle(surface, color,
                               (zone.x * 80 + self.screen_w / 2 - 70 +
                                self.offset_x,
                                zone.y * 150 + self.screen_h / 2 + 30 +
                                self.offset_y),
                               35, 0)

        self.draw_drones(zone, surface)

        pygame.draw.circle(surface, 'white',
                           (zone.x * 80 + self.screen_w / 2 - 70 +
                            self.offset_x,
                            zone.y * 150 + self.screen_h / 2 + 30 +
                            self.offset_y), 35, 3)
        zone_name = self.font2.render(f'{zone.name}', True, 'green')
        available_d = self.font2.render(
            'drones: '
            f'{len(zone.available_drones)}',
            True, 'white')
        capacity_d = self.font2.render(
            f'CAPACITY: {zone.metadata.max_drones}', True, 'white')
        cost = self.font2.render(
            f'COST: {zone.cost}', True, 'white')
        surface.blit(zone_name, (zone.x * 80 + self.screen_w / 2 -
                                 100 + self.offset_x,
                                 zone.y * 150 + self.screen_h / 2 + 70 +
                                 self.offset_y))
        surface.blit(available_d, (zone.x * 80 + self.screen_w / 2 - 100 +
                                   self.offset_x,
                                   zone.y * 150 + self.screen_h / 2 + 80 +
                                   self.offset_y))
        surface.blit(capacity_d, (zone.x * 80 + self.screen_w / 2 - 100 +
                                  self.offset_x,
                                  zone.y * 150 + self.screen_h / 2 + 90 +
                                  self.offset_y))
        surface.blit(cost, (zone.x * 80 + self.screen_w / 2 - 100 +
                            self.offset_x,
                            zone.y * 150 + self.screen_h / 2 + 100 +
                            self.offset_y))

    def draw_drones(self, zone: Zone, surface: Any) -> None:
        """
        Draws drones located within a specific zone.

        Args:
            zone: The zone where drones are located.
            surface: The Pygame surface to draw on.
        """
        if zone.available_drones:
            img = self.drone_img
            color = choice(['red', 'yellow', 'orange', 'white'])
            surface.blit(img, (zone.x * 80 + self.screen_w / 2 - 100 +
                               self.offset_x,
                               zone.y * 150 + self.screen_h / 2 +
                               self.offset_y))

            drone_info = self.font2.render(
                f'{[drone.id for drone in zone.available_drones]}',
                True, color)
            surface.blit(drone_info, (zone.x * 80 + self.screen_w / 2 - 100 +
                                      self.offset_x,
                                      zone.y * 150 + self.screen_h / 2 - 10 +
                                      self.offset_y))

    def connec_zones(self, connec: Connection, surface: Any) -> None:
        """
        Draws a line representing a connection between two zones.

        Also draws any drones currently traversing that connection.

        Args:
            connec: The Connection object to draw.
            surface: The Pygame surface to draw on.
        """
        pygame.draw.line(surface, (0, 56, 54),
                         (connec.zone1.x * 80 + self.screen_w / 2 + 25 - 100 +
                          self.offset_x,
                          connec.zone1.y * 150 + self.screen_h / 2 + 25 +
                          self.offset_y),
                         (connec.zone2.x * 80 + self.screen_w / 2 + 25 - 100 +
                          self.offset_x,
                          connec.zone2.y * 150 + self.screen_h / 2 + 25 +
                          self.offset_y),
                         5)
        drones_len: int = len(
            self.graph.connections[connec.zone1.name+'-'+connec.zone2.name].
            available_drones)
        if drones_len:
            img = self.drone_img

            zone1_x: int = (connec.zone1.x * 80 +
                            self.screen_w / 2 - 100
                            + self.offset_x)
            zone2_x: int = (connec.zone2.x * 80 +
                            self.screen_w / 2 - 100
                            + self.offset_x)
            x_diff: float = (zone2_x - zone1_x) / 2

            zone1_y: int = (connec.zone1.y * 150 +
                            self.screen_h / 2
                            + self.offset_y)
            zone2_y: int = (connec.zone2.y * 150 +
                            self.screen_h / 2
                            + self.offset_y)
            y_diff: float = (zone2_y - zone1_y) / 2
            surface.blit(img, (zone1_x + x_diff,
                               zone1_y + y_diff))

            connec_name = (connec.zone1.name + "-" +
                           connec.zone2.name)
            drones_list = (self.graph.connections[connec_name]
                           .available_drones)
            drone_info = self.font2.render(
                f'{[drone.id for drone in drones_list]}',
                True, 'white')
            surface.blit(drone_info, (zone1_x + x_diff + 20,
                                      zone1_y + y_diff))

    def run_gui(self) -> None:
        """
        Starts the main Pygame loop for the visualizer.

        This method handles user input, updates the simulation state
        per turn, and redraws the screen.
        """
        info: Any = pygame.display.Info()
        self.screen_w, self.screen_h = info.current_w, info.current_h
        screen: Any = pygame.display.set_mode((self.screen_w, self.screen_h),
                                              pygame.RESIZABLE)
        pygame.display.set_caption(
            '❣️❣️❣️ yousenna FLY-IN project ❣️❣️❣️')
        run: bool = True
        self.graph.remove_drones_from_all_zones_connecs()
        self.graph.move_all_drones_to_start_zone()
        nb_turnes = 0
        end_zone_name: str = self.graph.start_end_zones['end_hub']
        start_zone_name: str = self.graph.start_end_zones['start_hub']
        drones: deque[Drone] = self.graph.drones
        clock = pygame.time.Clock()

        while run:

            screen.fill((11, 0, 89))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            keys = pygame.key.get_pressed()

            if keys[pygame.K_SPACE]:
                sleep(0.2)
                end_zone = self.graph.zones[end_zone_name]
                if (len(end_zone.available_drones) !=
                   self.graph.nb_drones):
                    nb_turnes += 1
                    print(' '.join(self.graph.ft_turn(
                        drones, end_zone)))

            if keys[pygame.K_DOWN]:
                self.offset_y += 50
            if keys[pygame.K_UP]:
                self.offset_y -= 50
            if keys[pygame.K_LEFT]:
                self.offset_x -= 50
            if keys[pygame.K_RIGHT]:
                self.offset_x += 50
            if keys[pygame.K_TAB]:
                self.graph.remove_drones_from_all_zones_connecs()
                self.graph.move_all_drones_to_start_zone()
                drones = deque(self.graph.drones)
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
            clock.tick(8)

        pygame.QUIT
