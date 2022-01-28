#!/usr/bin/env python3.7

"""
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
"""

# packages
import pickle


class Saveable:

    def save(self, path: str):
        with open(path, 'wb') as file:
            pickle.dump(self, file)