from enum import Enum, unique

#%% Core (backend) functionality

@unique
class SetupMode(Enum):
    NEW = 0
    OLD = 1


@unique
class ConfigKey(Enum):
    MASTER = 'master'
    EXCEPTIONS = 'exceptions'


#%% Trace functionality

@unique
class DownSampleMode(Enum):
    KEEP = 0
    REMOVE = 1


class WriteMode(Enum): # note: NOT required to have unique values
    SECTIONWISE = '.txt'
    DATA = '.dat'


#%% Higher-level Manager functionality

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


#%% Fiber Position and Type

@unique
class FiberXYMode(Enum):
    config = 'fiber_xy'
    UNIFORM_DENSITY = 0  # all fascicles have same fiber DENSITY, randomized positions within each fascicle
    UNIFORM_COUNT = 1  # all fascicles have save fiber COUNT, same randomization of positions within each fascicle
    CENTROID = 2  # a single fiber per inner trace (endoneurium bundle?), located at each inner trace centroid
    WHEEL = 3  # 1) points on lines extending radially for each inner centroid, 2) offset inwards from boundary


@unique
class FiberZMode(Enum):
    config = 'fiber_z'
    EXTRUSION = 0
    LOFTED = 1


@unique
class ZOffsetMode(Enum):
    config = 'z_offset',
    UNIFORM = 0  # choose uniform offset (in JSON as 'fiber_z/offset'... 0.0 for node centered about z bounds)
    RANDOM = 1  # max range of +/- 1/2 segment length (internodal length for MRG)


@unique
class MyelinationMode(Enum):
    config = 'myel'
    UNMYELINATED = False
    MYELINATED = True


@unique
class MyelinatedFiberType(Enum):
    config = 'myel_fiber'
    NONE = None
    MRG = 0
    B_FIBER = 1


@unique
class UnmyelinatedFiberType(Enum):
    config = 'umyel_fiber'
    NONE = None
    SUNDT = 0
    TIGERHOLM = 1
    RATTAY = 2
    SCHILD = 3
