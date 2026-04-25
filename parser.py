# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  parser.py                                         :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: yousenna <yousenna@student.42.fr>         +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/03/15 07:33:01 by yousenna        #+#    #+#               #
#  Updated: 2026/04/25 10:04:47 by yousenna        ###   ########.fr        #
#                                                                           #
# ************************************************************************* #
from typing import Dict, List, Optional, Tuple, Union, Any
from enum import Enum
from math import inf
import os
from collections import deque


class ProporityError(Exception):
    pass


class MaxDronesError(Exception):
    pass


class ZoneTypes(Enum):
    NORMAL = 'normal'
    BLOCKED = 'blocked'
    RESTRICTED = 'restricted'
    PRIORITY = 'priority'


class ZoneMetaData:
    def __init__(self, line_nb: int, zone_type: Any = 'normal',
                 color: Optional[str] = None,
                 max_drones: Any = 1):
        self.line_number: int = line_nb
        self.zone_type: ZoneTypes = self._get_zone_type(zone_type)
        self.color: Optional[str] = self._get_color(color)
        self.max_drones: int = self._get_max_drones(max_drones)

    def __str__(self) -> str:
        return (f'|Zone Metadata| line number = {self.line_number} | '
                f'zone type = {self.zone_type} | '
                f'color = {self.color} | '
                f'max_drones = {self.max_drones} |')

    def __repr__(self) -> str:
        return self.__str__()

    def _get_zone_type(self, zone_type: str) -> ZoneTypes:
        try:
            valid_zone: ZoneTypes = ZoneTypes(zone_type)
        except ValueError as e:
            raise ValueError(f'at line {self.line_number}:'
                             f' Unsuport value for "zone" key [{e}]\n'
                             f'try one of those: {
                            [zone.value for zone in ZoneTypes]}'
                             )
        return valid_zone

    def _get_color(self, color: Optional[str]) -> Optional[str]:
        if color is None or color.isalpha():
            valid_color: Optional[str] = color
        else:
            raise ValueError(f'at line {self.line_number}:'
                             f' color is not valid single-word strings\n'
                             'try something like (red, bleu, green ....)'
                             )
        return valid_color

    def _get_max_drones(self, nb: Union[int, str]) -> int:
        try:
            valid_drones_nb: int = int(nb)
            if valid_drones_nb < 1:
                raise MaxDronesError(f'at line {self.line_number} '
                                     '"max_drones" value must be greater then'
                                     ' 0')
        except ValueError as e:
            raise ValueError(f'Error in line {self.line_number}:'
                             f' [{e}]')
        return valid_drones_nb


class Drone:
    def __init__(self, id: str):
        self.id: str = id
        self.restrected_target_zone: bool = False
        # self.trucked: bool = True
        # self.current_zone: str = ''

    def __str__(self) -> str:
        return (f'|id| = {self.id} | ')

    def __repr__(self) -> str:
        return self.__str__()


class Zone:
    def __init__(self, name: str, x: int, y: int, metadata: ZoneMetaData,
                 prefix: str):
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.metadata: ZoneMetaData = metadata
        self.cost = self._cost()
        self.prefix: str = prefix
        self.nighbors: List[Zone] = []
        # self.add_drone: bool = True
        self.available_drones: deque[Drone] = deque()
        self.restricted_drones: deque[Drone] = deque()

    def _cost(self) -> int:
        if self.metadata.zone_type == ZoneTypes('normal'):
            self.perfect: int = 1
            return 1
        if self.metadata.zone_type == ZoneTypes('restricted'):
            self.perfect: int = 2
            return 2
        if self.metadata.zone_type == ZoneTypes('priority'):
            self.perfect: int = 0
            return 1
        if self.metadata.zone_type == ZoneTypes('blocked'):
            self.perfect: int = inf
            return inf

    def __str__(self) -> str:
        return (
            f'|Zone info| name = {self.name} | '
            f'x = {self.x} | y = {self.y} | '
            f'metadata = {self.metadata} cost = {self.cost}|\n'
            f'|--> available drones: '
            f'{[drone for drone in self.available_drones]}\n\n'
        )

    def __repr__(self) -> str:
        return self.__str__()


class ConnecMetadata:
    def __init__(self, line_number: int, max_link_capacity: int = 1):
        self.line_number = line_number
        self.max_link_capacity: int = self._get_link_capacity(
            max_link_capacity)

    def __str__(self) -> str:
        return (
            '|Connection metadata info| max_link_capacity = '
            f'{self.max_link_capacity} | '
        )

    def _get_link_capacity(self, max_links: int) -> int:
        if (max_links < 1):
            raise MaxDronesError(f'at line {self.line_number}: '
                                 'max_drone_capacity must be greater then 0')
        return max_links


class Connection:
    def __init__(self, zone_1: Any, zone_2: Any, metadata: ConnecMetadata):
        self.zone1: Zone = zone_1
        self.zone2: Zone = zone_2
        self.metadata: ConnecMetadata = metadata

    def __str__(self) -> str:
        return (
            f'[{self.zone1.name}-{self.zone2.name}]'
            f'| Connection info| zone1 = {self.zone1} | '
            f'zone2 = {self.zone2} | '
            f'metadata = {self.metadata} |\n'
        )

    def __repr__(self) -> str:
        return self.__str__()


class Parser:
    def __init__(self, file_name: str) -> None:
        self.file_name: str = file_name
        self.start_end_zones_name: Dict[str, str] = {}
        self.zones: Dict[str, Zone] = {}
        # i will store all my connections in this instance atterbute
        self.connections: List[Connection] = []

    def parse_map(self) -> None:
        # check if file empty
        if not os.path.getsize(self.file_name):
            raise ValueError('Error file is empty')
        with open(self.file_name, 'r') as f:
            line_number: int = 0
            # parsing of first line must containe nb_lines
            for line in f:
                line = line.strip()
                line_number += 1
                if line.startswith('#') or not line:
                    continue
                else:
                    break
            self.nb_drones: int = self._get_nb_drones(line, line_number)

            zone_prefix: List[str] = []
            # parsing of zones
            for line in f:
                line = line.strip()
                line_number += 1
                if line.startswith('#') or not line:
                    continue
                if 'hub' in line:
                    zone_name, zone_obj = self._parse_zone(line, line_number,
                                                           self.zones,
                                                           zone_prefix)
                    self.zones[zone_name] = zone_obj
                # i need to parse first line that's has connection
                elif 'connection' in line:
                    self.connections.append(self._parse_connection(line,
                                                                   line_number
                                                                   ))
                    break
                else:
                    raise SyntaxError(f'at line {line_number}: '
                                      f'Unknowing syntax [{line.strip('\n')}]')

            if 'start_hub' not in zone_prefix:
                raise SyntaxError(f'at line {line_number} missing zone type\'s'
                                  ' prefix "start_hub" it should be before '
                                  'connections definetion')
            elif 'end_hub' not in zone_prefix:
                raise SyntaxError(f'at line {line_number} missing zone type\'s'
                                  ' prefix "end_hub" it should be before '
                                  'connections definetion')

            # parsing connection
            for line in f:
                line = line.strip()
                line_number += 1
                if line.startswith('#') or not line:
                    continue
                if 'connection' in line:
                    self.connections.append(
                        self._parse_connection(line, line_number)
                    )
                else:
                    raise SyntaxError(f'at line {line_number}: the line '
                                      'should contient "connection" or '
                                      'nothing')
            if not len(self.connections):
                raise SyntaxError('missing connections in your file')

    @staticmethod
    def _get_nb_drones(line: str, line_number: int) -> int:
        if 'nb_drones' not in line:
            raise ProporityError(f'at line {line_number}: first '
                                 'line must have nb_drones propority')
        if len(line.split(":")) != 2:
            raise SyntaxError(f'at line {line_number}: excpted '
                              'syntax for nb_drones must be like\n'
                              'nb_drones: <number>')
        if line.split(':')[0].strip() != 'nb_drones':
            raise SyntaxError(f'at line {line_number}: excpted '
                              'syntax for nb_drones must be like\n'
                              'nb_drones: <number>')
        try:
            nb_drones = int(line.split(':')[1])
        except ValueError as e:
            raise ValueError(f'at line {line_number}: {e}')
        if nb_drones <= 0:
            raise ValueError(f'at line {line_number}: nb_drones must be '
                             'postive integer')
        return nb_drones

    def _parse_zone(self, line: str, line_number: int,
                    zones: Dict[str, Zone], zone_types: List[str]
                    ) -> Tuple[str, Zone]:
        # check for start_hub, end_hub, or hub
        if ':' not in line:
            raise SyntaxError(f'at line {line_number} invalid syntax for '
                              'declaring a zone available syntaxs:\n'
                              'start_hub: <name> <x> <y> [metadata], for '
                              'starting zone or\n'
                              'end_hub: <name> <x> <y> [metadata], for '
                              'ending zone or\n'
                              'hub: <name> <x> <y> [metadata], for '
                              'regular zone\n')
        prefix, rest = line.split(':', 1)
        prefix = prefix.strip()
        if (len(line.split(":")) != 2) or (len(line.split(":")) == 2
           and prefix not in ['start_hub', 'end_hub', 'hub']):
            raise SyntaxError(f'at line {line_number}: excpted '
                              'syntax for zones must be like\n'
                              'start_hub: <name> <x> <y> [metadata], for '
                              'starting zone or\n'
                              'end_hub: <name> <x> <y> [metadata], for '
                              'ending zone or\n'
                              'hub: <name> <x> <y> [metadata], for '
                              'regular zone\n'
                              )
        if '[' in rest and ']' in rest:
            start_index = rest.index('[') + 1
            end_index = rest.index(']')
            if end_index < start_index:
                raise SyntaxError(f'at line {line_number} ] came '
                                  'before [')
            zone_metadata: Optional[str] = rest[start_index: end_index]
            if len(rest[end_index+1:].strip()) > 0:
                print(rest[end_index+1].strip())
                raise SyntaxError(f'at line {line_number} do not'
                                  ' write somthing after [metdata]')
            rest = rest[:start_index-1]
        elif '[' in rest or ']' in rest:
            raise SyntaxError(f'at line {line_number} '
                              'if you want to add metadata please put '
                              'it between [] and check if zone name '
                              'doesn\'t have "[" or "]"'
                              )
        else:
            zone_metadata = None
        zone_proporitys: List[str] = rest.split()
        if (len(zone_proporitys) > 3):
            raise SyntaxError(f'at line {line_number}: zone name has '
                              'space or syntax error it must be like\n'
                              'start_hub: <name> <x> <y> [metadata], for '
                              'starting zone or\n'
                              'end_hub: <name> <x> <y> [metadata], for '
                              'ending zone or\n'
                              'hub: <name> <x> <y> [metadata], for '
                              'regular zone\n'
                              )
        if len(zone_proporitys) < 3:
            raise SyntaxError(f'at line {line_number}: musing '
                              'name of zone or x or y, Expected syntax:\n'
                              'start_hub: <name> <x> <y> [metadata], for '
                              'starting zone or\n'
                              'end_hub: <name> <x> <y> [metadata], for '
                              'ending zone or\n'
                              'hub: <name> <x> <y> [metadata], for '
                              'regular zone\n'
                              )
        if prefix == 'start_hub' and 'start_hub' in zone_types:
            raise ValueError(f'at line {line_number}: the file must have '
                             'only one [start_hub] zone')
        if prefix == 'end_hub' and 'end_hub' in zone_types:
            raise ValueError(f'at line {line_number}: the file must have '
                             'only one [end_hub] zone.')
        zone_types.append(prefix)
        zone_name: str = zone_proporitys[0]
        if '-' in zone_name:
            raise SyntaxError('Invalid name of zone at line'
                              f' {line_number} should not have dashe')
        if zone_name in zones:
            raise ValueError(f'at line {line_number}: {zone_name}'
                             ' already exist')
        try:
            x: int = int(zone_proporitys[1])
            y: int = int(zone_proporitys[2])
        except ValueError as e:
            raise ValueError(f'at line {line_number} The zones '
                             f'coordinates must be integers: {e}')
        if prefix == 'start_hub' or prefix == 'end_hub':
            self.start_end_zones_name.update({prefix: zone_name})

        # parse metadata
        if not zone_metadata:
            return (zone_name,
                    Zone(zone_name, x, y, ZoneMetaData(line_number), prefix)
                    )
        else:
            support_metadata: List[str] = ['zone', 'color', 'max_drones']
            metadata_els: List[str] = zone_metadata.split()
            if len(metadata_els) > 3:
                raise ValueError(f'at line {line_number}: syntax error'
                                 ' or unsupport metadata, please check if '
                                 'you use supporting '
                                 'elements, color, zone, max_drones'
                                 'and check if you split key=value with space'
                                 'and no space between keys and values')
            if len(metadata_els) != len(set(metadata_els)):
                raise ValueError(f'at line {line_number}: check if '
                                 'no duplicatee of metadata')
            metadata_dict: Dict[str, str] = {}
            for data in metadata_els:
                if '=' in data:
                    key, value = data.split('=', 1)
                    if not len(key):
                        raise SyntaxError(f'at line {line_number}: '
                                          f'{value} missing it\'s '
                                          'key')
                    elif not len(value):
                        raise SyntaxError(f'at line {line_number}: '
                                          f'{key} missing it\'s '
                                          'value')
                    if key.strip() not in support_metadata:
                        raise ValueError(f'at line {line_number}: '
                                         'unsupport metadata element "'
                                         f'{key.strip()}" try '
                                         f'{support_metadata}'
                                         )
                    metadata_dict[key] = value
                else:
                    raise SyntaxError(f'at line {line_number}: [invalid '
                                      'syntax] missing key=value for metadata'
                                      ' of zone')

            zone: Optional[str] = metadata_dict.get('zone') if \
                metadata_dict.get('zone') else 'normal'
            color: Optional[str] = metadata_dict.get('color') if \
                'color' in metadata_dict else None
            max_drones: Union[Optional[str], int] = \
                metadata_dict.get('max_drones') if \
                'max_drones' in metadata_dict else 1

            return (zone_name, Zone(zone_name, x, y, ZoneMetaData(line_number,
                                    zone, color, max_drones), prefix))

    def _parse_connection(self, line: str, line_number: int) -> Connection:
        if ':' not in line:
            raise SyntaxError(f'at line {line_number}: invalid syntax \n'
                              'expected syntax: '
                              'connection: <zone1>-<zone2> [metadata]')
        prefix, rest = line.split(':', 1)
        if prefix.strip() != 'connection':
            raise SyntaxError(f'at line {line_number} connection syntax not'
                              ' like: \n'
                              'connection: <zone1>-<zone2> [metadata]')
        if '[' in line:
            if ']' not in line:
                raise SyntaxError(f'at line {line_number}: invalid syntax '
                                  'if you want to add metadata for this '
                                  'connection put it between []')
            start_index = rest.index('[')
            end_index = rest.index(']')
            if start_index > end_index:
                raise SyntaxError(f'at line {line_number}: invalid syntax '
                                  'if you want to add metadata for this '
                                  'connection put it between [], make sure '
                                  'you don\'t revers them')
            metadata = rest[start_index+1:end_index].strip()
            if len(rest[end_index+1:]) > 0:
                raise SyntaxError(f'at line {line_number}: you shouldn\'nt '
                                  'write any thing after metadata')

            rest = rest[:start_index]
        else:
            metadata = ''
        zones = rest
        if not zones:
            raise SyntaxError(f'at line {line_number} mising zones name: '
                              'valid syntax: \n'
                              'connection: <zone1>-<zone2> [metadata]')
        if '-' not in zones:
            raise SyntaxError(f'at line {line_number} missing dashes between'
                              ' two zones valid syntax: \n'
                              'connection: <zone1>-<zone2> [metadata]')
        zone1, zone2 = zones.split('-', 1)
        zone1 = zone1.strip()
        zone2 = zone2.strip()
        if '-' in zone2:
            raise SyntaxError(f'at line {line_number} multiple dashes at '
                              'same line')
        if zone1 not in self.zones:
            raise ValueError(f'at line {line_number}: Unknowing zone '
                             f'"{zone1}" please make shure you decleare '
                             'this zone befor use it')
        if zone1 == zone2:
            raise SyntaxError(f'at line {line_number}: first zone must be '
                              'deferance then secand zone')
        if zone2 not in self.zones:
            raise ValueError(f'at line {line_number}: Unknowing zone '
                             f'"{zone2}" please make shure you decleare '
                             'this zone befor use it')

        if self.connections:
            available_conections: List[List[str]] = [
                [connec.zone1.name, connec.zone2.name]
                for connec in self.connections
            ]
        else:
            available_conections = []

        if ([zone1, zone2] in available_conections
           or [zone2, zone1] in available_conections):
            raise ValueError(f'at line {line_number} connection already'
                             ' exsiste')

        if metadata:
            if '=' not in metadata:
                raise SyntaxError(f'at line {line_number}: you must to put'
                                  ' your metadata in this syntax [key=value]'
                                  )
            key, value = metadata.split('=', 1)
            if key != 'max_link_capacity':
                raise ValueError(f'at line {line_number}: unsupport {key}'
                                 ' for metadata of connection please try '
                                 '[max_link_capacity]')
            if '=' in value:
                raise SyntaxError(f'at line {line_number}: we support only '
                                  'one metadata for connections '
                                  '"max_link_capacity"')
            try:
                valid_value: int = int(value)
            except ValueError as e:
                raise ValueError(f'at line {line_number} '
                                 'max_link_capacity value must be valid '
                                 f'integer: {e}')
            return Connection(self.zones.get(zone1),
                              self.zones.get(zone2),
                              ConnecMetadata(line_number, valid_value))
        return Connection(self.zones.get(zone1),
                          self.zones.get(zone2),
                          ConnecMetadata(line_number))


if __name__ == "__main__":
    p = Parser('test.txt')
    p.parse_map()
    print('nb_drones = ', p.nb_drones)
    print('zones = ', *[[zone_name, zone_obj.__str__()]
                        for (zone_name, zone_obj) in p.zones.items()],
          sep='\n')
    print('connections = \n', *[[conec]
                                for conec in p.connections], sep='\n')
    print('start vs end zones: ', p.start_end_zones_name)
