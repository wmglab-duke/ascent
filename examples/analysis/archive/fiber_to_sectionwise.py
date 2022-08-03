#!/usr/bin/env python3.7

"""
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent


"""

import os
import re
import sys

import numpy as np

usage: str = (
    'USAGE: ./fiber_to_sectionwise.py <[xyz]*> <source_path.dat> <target_path.txt>\n'
    'notes: (1) xyz expr. is regex (2) must type ".dat" and ".txt" -- these are convention)'
)

if len(sys.argv) != 4:
    print(f'Invalid argument count: {len(sys.argv)}\n{usage}')
    sys.exit()

options: str = sys.argv[1]
source: str = sys.argv[2]
target: str = sys.argv[3]
target_dir, _ = os.path.split(target)

if not re.match('[xyz]*', options):
    print(f'Invalid output options: {options}\n{usage}')
    sys.exit()

if len(options) not in [1, 2, 3]:
    print(f'Invalid output options length: {len(options)}\n{usage}')
    sys.exit()

for name, value in zip(['source', 'target directory'], [source, target_dir]):
    if not os.path.exists(value):
        print(f'Invalid path for {name}: {value}\n{usage}')
        sys.exit()

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
            line = f'{line}\t{addition}'

        handle.write(f'{line[1:]}\n')

print(f'Sectionwise file written to: {target}')
