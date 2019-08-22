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


class WriteMode(Enum):  # note: NOT required to have unique values
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
    parameters = 'fiber_xy_parameters'

    UNIFORM_DENSITY = 0  # all fascicles have same fiber DENSITY, randomized positions within each fascicle
    UNIFORM_COUNT = 1  # all fascicles have save fiber COUNT, same randomization of positions within each fascicle
    CENTROID = 2  # a single fiber per inner trace (endoneurium bundle?), located at each inner trace centroid
    WHEEL = 3  # 1) points on lines extending radially for each inner centroid, 2) offset inwards from boundary


@unique
class FiberZMode(Enum):
    config = 'fiber_z'
    parameters = 'fiber_z_parameters'

    EXTRUSION = 0
    LOFTED = 1


@unique
class ZOffsetMode(Enum):
    config = 'z_offset'
    parameters = 'z_offset_parameters'

    UNIFORM = 0  # choose uniform offset (in JSON as 'fiber_z/offset'... 0.0 for node centered about z bounds)
    RANDOM = 1  # max range of +/- 1/2 segment length (internodal length for MRG)


@unique
class MyelinationMode(Enum):
    config = 'myel'
    parameters = 'fiber_type_parameters'

    MYELINATED = True
    UNMYELINATED = False


@unique
class MyelinatedFiberType(Enum):
    config = 'myel_fiber'

    NONE = None
    MRG = 0
    B_FIBER = 1


@unique
class UnmyelinatedFiberType(Enum):
    config = 'unmyel_fiber'

    NONE = None
    SUNDT = 0
    TIGERHOLM = 1
    RATTAY = 2
    SCHILD = 3


#%% Waveforms

@unique
class WaveformMode(Enum):
    config = 'waveform'
    parameters = 'waveform_parameters'
    global_parameters = 'global'

    MONOPHASIC_PULSE_TRAIN = 0
    SINUSOID = 1
    BIPHASIC_FULL_DUTY = 2
    BIPHASIC_PULSE_TRAIN = 3


#%% Cuffs

@unique
class CuffInnerMode(Enum):
    config = 'cuff_inner'
    parameters = 'cuff_inner_parameters'

    CIRCLE = 0
    BOUNDING_BOX = 1

class CuffMode(Enum):
    config = 'cuff_mode'
    parameters = 'cuff_parameters'

    BIPOLAR_EMBEDDED_RIBBON = 0
    BIPOLAR_EXPOSED_WIRE = 1
    LIVANOVA = 2
    ENTEROMEDICS = 3
    IMTHERA = 4


#%% Templates

@unique
class TemplateMode(Enum):
    path = '.templates'
    ELECTRODE_INPUT = 'electrode_input.json'
