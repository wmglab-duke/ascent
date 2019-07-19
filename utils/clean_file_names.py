#!/usr/bin/env python3.7

# Author: Jake Cariello
# Date: July 15, 2019
# General Purpose: Remove annoying slide code from start of every slide name.


import os
import re

dir_to_parse = '/Users/jakecariello/Box/Histology/UW-Madison/Segmentations/Cassettes/VN1_A'

prefixes = ['19P866_', 'Pig19P866_']

remove_keys = ['.dxf']

for root, dirs, files in os.walk(dir_to_parse):
    for file in files:
        for prefix in prefixes:
            if re.match(prefix, file) is not None:
                # remove leading code (separated by '_') and any extra '_'
                new_file = '_'.join([f for f in file.split('_')[1:] if f is not ''])
                os.rename('{}/{}'.format(root, file),
                          '{}/{}'.format(root, new_file))

        for key in remove_keys:
            if re.search(key, file) is not None:
                os.remove('{}/{}'.format(root, file))

