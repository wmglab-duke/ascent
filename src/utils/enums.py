from enum import Enum, unique


@unique
class SetupMode(Enum):
    NEW = 0
    OLD = 1


@unique
class ConfigKey(Enum):
    MASTER = 'master'
    EXCEPTIONS = 'exceptions'


@unique
class DownSampleMode(Enum):
    KEEP = 0
    REMOVE = 1


class WriteMode(Enum): # note: NOT required to have unique values
    SECTIONWISE = '.txt'
    DATA = '.dat'

@unique
class ReshapeNerveMode(Enum):
    CIRCLE = 0
    ELLIPSE = 1

@unique
class MaskInputMode(Enum):
    INNERS = 0
    OUTERS = 1
    INNER_AND_OUTER_SEPARATE = 2
    INNER_AND_OUTER_COMPILED = 3

