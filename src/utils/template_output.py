#!/usr/bin/env python3.7

"""Defines the TemplateOutput class.

The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
"""

import json
from typing import Union


class TemplateOutput:
    """Represent the output of a populated template."""

    @staticmethod
    def write(data: Union[list, dict], dest_path):
        """Write JSON object to file.

        :param data: The data to write.
        :param dest_path: The destination path.
        """
        with open(dest_path, "w") as handle:
            handle.write(json.dumps(data, indent=2))
