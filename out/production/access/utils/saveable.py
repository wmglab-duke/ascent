#!/usr/bin/env python3.7

# packages
import pickle


class Saveable:

    def save(self, path: str):
        file = open(path, 'wb')
        pickle.dump(self, file)
