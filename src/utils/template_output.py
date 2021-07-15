#!/usr/bin/env python3.7

"""
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE.txt and README.txt files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
"""

import json
import os
from typing import Union

from .enums import TemplateMode


class TemplateOutput:

    @staticmethod
    def read(mode: TemplateMode) -> Union[list, dict]:
        path = os.path.join(TemplateMode.path.value, mode.value)
        with open(path, "r") as handle:
            return json.load(handle)

    @staticmethod
    def write(data: Union[list, dict], dest_path):
        with open(dest_path, "w") as handle:
            handle.write(json.dumps(data, indent=2))
