#!/usr/bin/env python3.7

import sys
import os

import numpy as np

usage: str = 'USAGE: ./fiber_to_sectionwise <source_path.dat> <target_path.txt>\n' \
             '(must type ".dat" and ".txt" -- these are convention)'

if len(sys.argv) != 3:
    print('Invalid argument count: {}\n{}'.format(len(sys.argv), usage))
    exit()

source: str = sys.argv[1]
target: str = sys.argv[2]
target_dir, _ = os.path.split(target)

for name, value in zip(['source', 'target directory'], [source, target_dir]):
    if not os.path.exists(value):
        print('Invalid path for {}: {}\n{}'.format(name, value, usage))

data: np.ndarray = np.loadtxt(source, skiprows=1)

print(data)

with open(target, 'w+') as handle:
    # write coordinates
    handle.write('%% Coordinates\n')
    for i in range(len(data)):
        handle.write('{}\t{}\n'.format(data[i][0], data[i][1]))

print('Sectionwise2d file written to: {}'.format(target))
