#!/usr/bin/env python3.7

import sys
import os
import re

import numpy as np

usage: str = 'USAGE: <[xyz]*> ./fiber_to_sectionwise <source_path.dat> <target_path.txt>\n' \
             'notes: (1) xyz expr. is regex (2) must type ".dat" and ".txt" -- these are convention)'

if len(sys.argv) != 4:
    print('Invalid argument count: {}\n{}'.format(len(sys.argv), usage))
    exit()

options: str = sys.argv[1]
source: str = sys.argv[2]
target: str = sys.argv[3]
target_dir, _ = os.path.split(target)

if not re.match('[xyz]*', options):
    print('Invalid output options: {}\n{}'.format(options, usage))
    exit()

if not len(options) not in [1, 2, 3]:
    print('Invalid output options length: {}\n{}'.format(len(options), usage))
    exit()

for name, value in zip(['source', 'target directory'], [source, target_dir]):
    if not os.path.exists(value):
        print('Invalid path for {}: {}\n{}'.format(name, value, usage))
        exit()

data: np.ndarray = np.loadtxt(source, skiprows=1)

print(data)

with open(target, 'w+') as handle:
    # write coordinates
    handle.write('%% Coordinates\n')
    for i in range(len(data)):
        line = ''
        for char in options:
            addition = ''
            if char == 'x':
                addition = str(data[i][0])
            if char == 'y':
                addition = str(data[i][1])
            if char == 'z':
                addition = str(data[i][2])
            line = '{}\t{}'.format(line, addition)

        handle.write('{}\n'.format(line[1:]))

print('Sectionwise file written to: {}'.format(target))
