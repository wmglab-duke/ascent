#!/usr/bin/env python3.7

"""Defines the Saveable class.

The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
"""


import pickle


class Saveable:
    """Class that, when inherited, allows pickle to save the object."""

    def save(self, path: str):
        """Save the object to the specified path.

        :param path: The path to save the object to.
        """
        with open(path, 'wb') as file:
            pickle.dump(self, file)
