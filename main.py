# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  main.py                                           :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: yousenna <yousenna@student.42.fr>         +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/03/29 12:40:44 by yousenna        #+#    #+#               #
#  Updated: 2026/03/29 19:09:38 by yousenna        ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

from parser import Parser
from sys import argv, exit

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
        try:
            p = Parser(file)
            p.parse_map()
            graph = 
            
        except Exception as e:
            print(e.__class__.__name__, e)
            exit(1)
    else:
        print('Error invalid syntax try:\n'
              'python main.py map_file_example.txt\nor:\n'
              'python main.py map_file_example.txt --visual')
        
        # print(graph.file_name)
    
    # print(flag)
        
    # print(file)
            
    # print(len(argv))