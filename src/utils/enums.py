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
    config = 'reshape_nerve'
    CIRCLE = 0
    ELLIPSE = 1


@unique
class MaskInputMode(Enum):
    config = 'mask_input'
    INNERS = 0
    OUTERS = 1
    INNER_AND_OUTER_SEPARATE = 2
    INNER_AND_OUTER_COMPILED = 3


@unique
class MaskFileNames(Enum):
    RAW = 'r.tif'
    COMPILED = 'c.tif'
    INNERS = 'i.tif'
    OUTERS = 'o.tif'
    SCALE_BAR = 's.tif'
    NERVE = 'n.tif'


@unique
class NerveMode(Enum):
    config = 'nerve'
    PRESENT = 1
    NOT_PRESENT = 0


@unique
class DeformationMode(Enum):
    config = 'deform'
    NONE = None
    JITTER = 0
    PHYSICS = 1


