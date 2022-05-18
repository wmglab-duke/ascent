#!/usr/bin/env python3.7

"""
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
"""

# packages
import json
import os
from src.utils import Exceptionable, SetupMode

class Validatable(Exceptionable):

    def __init__(self):
        # initialize Exceptionable super class
        Exceptionable.__init__(self, SetupMode.NEW)

    def validate_cuff_configs(self, path: str):
        names = []
        codes = []
        codematch = {}
        for cuff in [x for x in os.listdir(path) if x.endswith('.json')]:
            names.append(cuff)
            with open(os.path.join(path,cuff),'r') as f:
                cuffcon = json.load(f)
                codes.append(cuffcon['code'])
        repeatname = set([x for x in names if names.count(x) > 1])
        repeatcode = set([x for x in codes if codes.count(x) > 1])
        if len(repeatname) > 0:
            print('Cuff config names duplicated: {}'.format(repeatname))
            self.throw(9001)
        if len(repeatcode) > 0:
            print('Cuff config codes duplicated: {}'.format(repeatcode))
            self.throw(9001)