# sim.json

Named file: `config/user/sims/<sim_index>.json`

## Purpose

Instructs the pipeline on which user-defined parameters to
use in constructing NEURON simulation directories (**_Sim_**). We
provide parameterized control of cuff electrode contact weighting,
fiber model and placement in the FEM, extracellular stimulation
waveform, intracellular stimulation, flags to indicate which
outputs to save (e.g., state variables of channel gating mechanisms,
transmembrane potential, intracellular stimulation), and stimulation
threshold-finding protocol ([Simulation Protocols](../../Running_ASCENT/Info.md#simulation-protocols)).

## Syntax

To declare this entity in `config/user/sims/`, use the
following syntax:

```javascript
{
  "pseudonym": String,
  "n_dimensions": Integer,
  "active_srcs": {
    "CorTec300.json": [[Double, Double]], // for example
    "cuff_index": Integer // Correlates with cuff index assigned to cuff configs in model.json
  },
  "active_recs": {
    "cyl_MicroLeads_300t.json":[[Double, Double, Double]], // for example
    "cuff_index": Integer
  },
  "fibers": {
    "mode": String,
    "xy_trace_buffer": Double,
    "z_parameters": {

      // EXAMPLE diameter parameter for defining fixed diameter fibers
      "diameter": [Double],

      // EXAMPLE diameter parameter for TRUNCHNORM (i.e., diameters from a truncated normal
      // distribution) which is only compatible for "MRG_INTERPOLATION" myelinated or
      // unmyelinated fiber types)
      "diameter":{
        "mode": "TRUNCNORM",
        "mu": Double,
        "std": Double,
        "n_std_limit": Double,
        "seed": Integer
      },

      // EXAMPLE diameter parameter for UNIFORM (i.e., diameters from a uniform
      // distribution) which is only compatible for "MRG_INTERPOLATION" myelinated or
      // unmyelinated fiber types)
      "diameter":{
        "mode": "UNIFORM",
        "upper": Double,
        "lower": Double,
        "seed": Integer
      },

      "mode": String,
      "fiber_z_shift": Integer,
      "min": Double,
      "max": Double,
      "full_nerve_length": Boolean,
      "offset": Double, // or "random" for random jitter within +/- 0.5 internodal length
      "absolute_offset": Double,
      "seed": Integer
    },

    // EXAMPLE XY Parameters for CENTROID (from best-fit ellipse of the Trace)
    "xy_parameters": {
      "mode": "CENTROID"
    },

    // EXAMPLE XY Parameters for UNIFORM_COUNT
    "xy_parameters": {
      "mode": "UNIFORM_COUNT",
      "count": Integer,
      "seed": Integer
    },

    // EXAMPLE XY Parameters for WHEEL
    "xy_parameters": {
      "mode": "WHEEL",
      "spoke_count": Integer,
      "point_count_per_spoke": Integer,
      "find_centroid": Boolean, // centroid of inner polygon
      "angle_offset": Double,
      "angle_offset_is_in_degrees": Boolean
    },

    // EXAMPLE XY Parameters for EXPLICIT
    "xy_parameters": {
      "mode": "EXPLICIT",
      "explicit_fiberset_index" : Integer
    },

    // EXAMPLE XY Parameters for EXPLICIT_3D
    "xy_parameters": {
      "mode": "EXPLICIT_3D",
      "explicit_fiberset_index" : Integer
    },

    // EXAMPLE XY Parameters for UNIFORM_DENSITY
    "xy_parameters": {
      "mode": "UNIFORM_DENSITY",
      "top_down": Boolean,
      // top_down is true
      "target_density": Double,
      "minimum_number": Integer,
      // top_down is false
      "target_number": Integer,
      "maximum_number": Integer,
      // for both top_down is true and false
      "seed": Integer
    }
  },
  "waveform": {
    "global": {
      "dt": Double,
      "on": Double,
      "off": Double,
      "stop": Double
    },

    // EXAMPLE WAVEFORM for MONOPHASIC_PULSE_TRAIN
    "MONOPHASIC_PULSE_TRAIN": {
      "pulse_width": Double,
      "pulse_repetition_freq": Double,
      "digits": Integer
    },

    // EXAMPLE WAVEFORM for SINUSOID
    "SINUSOID": {
      "pulse_repetition_freq": Double,
      "digits": Integer
    },

    // EXAMPLE WAVEFORM for BIPHASIC_FULL_DUTY
    "BIPHASIC_FULL_DUTY": {
      "pulse_repetition_freq": Double,
      "digits": Integer
    },

    // EXAMPLE WAVEFORM for BIPHASIC_PULSE_TRAIN
    "BIPHASIC_PULSE_TRAIN": {
      "pulse_width": Double,
      "inter_phase": Double,
      "pulse_repetition_freq": Double,
      "digits": Integer
    },

    // EXAMPLE WAVEFORM for BIPHASIC_PULSE_TRAIN_Q_BALANCED_UNEVEN_PW
    "BIPHASIC_PULSE_TRAIN_Q_BALANCED_UNEVEN_PW": {
      "pulse_width_1": Double,
      "pulse_width_2": Double,
      "inter_phase": Double,
      "pulse_repetition_freq": Double,
      "digits": Integer
    },

    // EXAMPLE WAVEFORM for EXPLICIT
    "EXPLICIT": {
      "index": Integer,
      "dt_atol": Double,
      "period_repeats ": Integer
    }
  },
  "intracellular_stim": {
    "times": {
      "pw": Double,
      "IntraStim_PulseTrain_delay": Double,
      "IntraStim_PulseTrain_dur": Double
    },
    "pulse_repetition_freq": Double,
    "amp": Double,
    "ind": Integer
  },
  "saving": {
    "aploctime": Boolean,
    "space": {
      "vm": Boolean,
      "gating": Boolean,
      "times": [Double],
    },
    "time": {
      "vm": Boolean,
      "gating": Boolean,
      "istim": Boolean,
      "locs": [Double] OR String
    },
    "end_ap_times": {
      "loc_min": Double,
      "loc_max": Double,
      "threshold": Double
    }
    "runtimes": Boolean,
    "3D_fiber_intermediate_data": Boolean
  },

  // EXAMPLE PROTOCOL for FINITE_AMPLITUDES
  "protocol": {
    "mode": "FINITE_AMPLITUDES",
    "initSS": Double,
    "dt_initSS": Double,
    "amplitudes": [Double, Double, ...],
    "threshold": {
      "value": Double,
      "ap_detect_location": Double
    }
  },

  // EXAMPLE PROTOCOL for ACTIVATION_THRESHOLD
  "protocol": {
    "mode": "ACTIVATION_THRESHOLD", //String
    "initSS": Double,
    "dt_initSS": Double,
    "threshold": {
      "value": Double,
      "ap_detect_location": Double
    },
    "bounds_search": {
      "mode": String,
      "top": Double,
      "bottom": Double,
      "step": Double
    },
    "termination_criteria": {
      "mode": "ABSOLUTE_DIFFERENCE",
      "percent": Double
    }
  },

  // EXAMPLE PROTOCOL for BLOCK_THRESHOLD
  "protocol": {
    "mode": "BLOCK_THRESHOLD", // String
    "initSS": Double,
    "dt_initSS": Double,
    "threshold": {
      "value": Double,
      "ap_detect_location": Double
    },
    "bounds_search": {
      "mode": String,
      "top": Double,
      "bottom": Double,
      "step": Double
    },
    "termination_criteria": {
      "mode": String,
      "percent": Double
    }
  },
  "supersampled_bases": {
    "generate": Boolean,
    "use": Boolean,
    "dz": Double,
    "source_sim": Integer
  }
}
```

## Properties

`"pseudonym"`: This value (String) informs pipeline print statements, allowing
users to better keep track of the purpose of each configuration file. Optional.

`“n_dimensions”`: The value (Integer) is the number of parameters in
**_Sim_** for which a list is provided rather than a single value. The
user sets the number of parameters they are looping over (e.g., if
looping over waveform pulse width and fiber diameter, `n_dimensions = 2`). We included this control to prevent the user from accidentally
creating unintended NEURON simulations. The pipeline will only loop over
the first n-dimensions. Required.

`“active_srcs”`: The value is a JSON Object containing key-value pairs of
contact weightings for preset stimulation cuffs. Each value (`List[List[Double]]`)
is the contact weighting used to make extracellular potentials inputs
to NEURON simulations. The order of weights matches the order of parts
containing point current sources. The values should not exceed +/-1 in magnitude,
otherwise an error is thrown. For monopolar cuff electrodes, the value
should be either +1 or -1. For cuff electrodes with more than one
contact (2+), the sum of weightings should be +1, -1, or 0. Required. The potentials/ for a single
fiber are calculated in the following way for an example weighting:

`"example_cuff_preset.json": [[1, -1]]` // [[weight<sub>1</sub> (for src 1 on),
weight<sub>2</sub> (for src 2 on)]]

$$V_{e}=(\textrm{amplitude})*\textrm{potentials}$$

$$\textrm{potentials}=(\textrm{weight}_{1})*\textrm{bases}_{1}(x,y,z)+(\textrm{weight}_{2})*\textrm{bases}_{2}(x,y,z)$$

The value of potentials/ is applied to a model fiber in NEURON
multiplied by the stimulation amplitude, which is either from a list of
finite amplitudes or a bisection search for thresholds ([Simulation Protocols](../../Running_ASCENT/Info.md#simulation-protocols))

$$\textrm{potentials}=(1)*\textrm{bases}_{1}(x,y,z)+(-1)*\textrm{bases}_{2}(x,y,z)$$

- `“cuff_index”`: The value (Integer) used to designate which cuff will be used for
  stimulation and which cuff will be used for recording. The index value must correspond to the “index” value in the Model "cuff" configuration. Required.

`“active_recs”`: The JSON Object value serves the same purpose as `active_srcs`, but provides contact weightings for preset cuffs used for recording. Only required when modeling a recording cuff in the Model configurations.

- `“cuff_index”`: The value (Integer) used to designate which cuff will be used for
  stimulation and which cuff will be used for recording. The index value must correspond to the “index” value in the Model "cuff" configuration. Required.

`“fibers”`: The value is a JSON Object containing key-value pairs that
define how potentials are sampled in the FEM for application as
extracellular potentials in NEURON (i.e., the Cartesian coordinates of
the midpoint for each compartment (i.e., section or segment) along the
length of the fiber). Required.

- `“mode”`: The value (String) is the “FiberGeometry” mode that tells
  the program which fiber geometries to simulate in NEURON ([NEURON Fiber Models](../../Running_ASCENT/Info.md#implementation-of-neuron-fiber-models)). Required.

  - As listed in [Enums](../../Code_Hierarchy/Python.md#enums), known modes include

    - `“MRG_DISCRETE”` (published MRG fiber model)

    - `“MRG_INTERPOLATION”` (interpolates the discrete diameters
      from published MRG fiber models)

    - `SMALL_MRG_INTERPOLATION_V1` (interpolates diameters from published literature data on small myelinated fibers; used by {cite:p}`Pena2024` to model myelinated fibers with >1.011 um diameter; uses the same ion channels as MRG_DISCRETE and MRG_INTERPLOATION, but decreases the maximum conductance of sodium ion channels and increases the maximum conductance of potassium ion channels to ensure one action potential per stimulus pulse.)

    - `“TIGERHOLM”` (published C-fiber model)

    - `“SUNDT”` (published C-fiber model)

    - `“RATTAY”` (published C-fiber model)

  - For a user to simulate a novel fiber type using the pipeline,
    they must define the spatial discretization of points within the
    `config/system/fiber_z.json` file to match the dimensions of the
    fiber compartments connected in NEURON. The “FiberGeometry” mode
    and parameters in the “fibers” JSON Object in **_Sim_** must
    match the keys in `config/system/fiber_z.json` to select and
    define a fiber type (e.g., MRG requires specification of fiber
    “diameters”).

- `“xy_trace_buffer”`: The value (Double, units: micrometer) indicates
  the minimum required distance between the (x,y)-coordinates of a
  given fiber and the fascicle's inner boundary. Since the domain boundaries
  are modeled in COMSOL as an interpolation curve, the exact
  morphology boundary coordinates read into COMSOL will be very close
  to (but not exactly equal to) those used in Python to seed fiber
  locations. To protect against instances of fibers falling within the
  nerve boundary traces in the exact Python traces, but not in
  COMSOL’s interpolation of those traces, we provided this
  parameter. Required.

- `“z_parameters”`: The value is a JSON Object containing key-value
  pairs to instruct the system in seeding fibers along the length of
  the nerve. Required.

  - `“diameter”` The value can take multiple forms to define the fiber diameter that the user is simulating in NEURON ([NEURON Fiber Models](../../Running_ASCENT/Info.md#implementation-of-neuron-fiber-models)). The value can control simulation of either fixed diameter fibers or fibers chosen from a distribution of diameters (note simulating a distribution of fiber diameters is only compatible with `“MRG_INTERPOLATION”`myelinated or unmyelinated fiber types, not `“MRG_DISCRETE”`). In **_Sim_**, only one mode of defining fiber diameters can be used. Required.

    - Fixed diameter: the value (Double or List[Double], units: micrometer) is the diameter of all fibers within the model. If using with `“MRG_DISCRETE”`, the diameters must be members of the set of published diameters.
    - Distribution of diameters: the value is a dictionary of key-value pairs to define the distribution of diameters based on the `“mode”` parameter, which can be either `“TRUNCNORM”` or `“UNIFORM”`.
      - `“TRUNCNORM”`
        - `“mode”`: “TRUNCNORM” (String). Required.
        - `“mu”`: The value (Double, units micrometer) is the mean diameter of the truncated normal distribution. Required.
        - `“std”`: The value (Double, units micrometer) is the diameter standard deviation of the truncated normal distribution. Required.
        - `“n_std_limit”`: The value (Double) is the number of standard deviations from the mean to bound the truncated normal distribution. Required.
        - `“seed”`: The value (Integer, unitless) seeds the random number generator before sampling fiber diameters.
      - `“UNIFORM”`
        - `“mode”`: `UNIFORM”` (String). Required.
        - `“upper”`: The value (Double, units micrometer) is the upper limit on the distribution of diameters. Required.
        - `“lower”`: The value (Double, units micrometer) is the lower limit on the distribution of diameters. Required.
        - `“seed”`: The value (Integer) seeds the random number generator before sampling fiber diameters.

  - `“mode”`: The value (String) is the `“FiberZMode”` that tells the program how to seed fiber z-locations along the length of the FEM model. Required.

    As listed in [Enums](../../Code_Hierarchy/Python.md#enums), implemented modes include

    - `“EXTRUSION”`: Creates straight fibers along the length of the model by extruding the xy- fiber locations defined by `“FiberXYMode”`.

    - `“EXPLICIT”`: Creates curved fibers within a 2D extrusion model by importing explicit 3D fiber coordinates from a file. When this mode is used, `"FiberXYMode"` must be `"EXPLICIT_3D"`.

      - `“fiber_z_shift"`: The value (Integer) specifies the longitudinal shift of the fiber coordinates from the model's center. This is shift is only applicable if the fibers are shorter than the model and are being extruded; the fiber_z_shift must be equal to or less than the extrusion length, such that all user-provided fiber coordinates remain within the model length. (optional)

  - `“min”`: the value (Double or List\[Double\], units: micrometer)
    is the distal extent of the seeded fiber along the length of the
    nerve closer to z = 0. Optional: if min and max are not both
    provided then the fiber length is assumed to be the proximal
    medium length (see `model.json`).

  - `“max”`: The value (Double or List\[Double\] , units: micrometer)
    is the distal extent of the seeded fiber along the length of the
    nerve closer to z = length of the proximal medium (as defined in
    `model.json`, the length of the nerve). Optional: if min and max
    are not both provided then the fiber length is assumed to be the
    proximal medium length by default.

  - `full_nerve_length`: (Boolean) Optional. If true, suppresses the warning message associated with using the full length nerve when `"min"` and `"max"` are not defined. Must be false or not defined if `"min"` and `"max"` are defined.

  - `“offset”`: The value (Double or String) is the fraction
    of the node-node length (myelinated fibers) or segment length
    (unmyelinated fibers) that the center coordinate of the fiber is
    shifted along the z-axis from the longitudinal center of the
    proximal medium. If the value is "random", the offset will
    be randomly selected between +/- 0.5 section/segment length; to
    avoid the randomized longitudinal placement, set the offset
    value to ‘0’ for no offset.

  - `“absolute_offset”`: The value (Double) is the distance (micrometers) that the center coordinate of the fiber is
    shifted along the z-axis from the longitudinal center of the
    proximal medium. This value is additive with `"offset"`.
    The shift is with respect to the model center. If a negative value is passed, the fiber will be shifted in the -z direction.
    Any offset from this parameter is cumulative with that from `"offset"`.

  - `“seed”`: The value (Integer) seeds the random number generator
    before any random offsets are created. Required only if “offset”
    is not defined, in which case the program will use a random
    offset.

- `“xy_parameters”`: The value is a JSON Object containing key-value
  pairs to instruct the system in seeding fiber locations at which to
  sample potentials inside fascicle inners in the nerve cross-section ([Fig 3B](https://doi.org/10.1371/journal.pcbi.1009285.g003)). Include only _one_ version of this block in your `sim.json`
  file. Required.

  `“mode”`: The value (String) is the `“FiberXYMode”` that tells the
  program how to seed fiber locations inside each fascicle inner in the nerve
  cross-section. Required.

- As listed in [Enums](../../Code_Hierarchy/Python.md#enums), known modes include

  - `“CENTROID”`: Place one fiber at the centroid (i.e., from the
    best-fit ellipse of the inner) of each inner.

    - No parameters required.

  - `“UNIFORM_COUNT”`: Randomly place the same number of fibers in
    each inner, regardless of inner’s size.

    - `“count”`: The value (Integer) is the number of fibers per
      inner. Required.

    - `“seed”`: The value (Integer) is the seed for the random
      number generator that is instantiated before the point
      picking algorithm for fiber (x,y)-coordinates starts.
      Required.

  - `“WHEEL”`: Place fibers in each inner following a pattern of
    radial spokes out from the geometric centroid.

    - `“spoke_count”`: The value (Integer) is the number of radial
      spokes. Required.

    - `“point_count_per_spoke”`: The value (Integer) is the
      number of fibers to place on each spoke out from the
      centroid (i.e., excluding the centroid). Required.

    - `“find_centroid”`: The value (Boolean), if true, tells the
      program to include the geometric centroid as a fiber
      coordinate. Required.

    - `“angle_offset”`: The value (Double, either degrees or
      radians depending on next parameter,
      `“angle_offset_is_in_degrees”`) sets the direction of
      the first spoke in the wheel. The rest of the spokes are
      equally spaced (radially) based on the “spoke_count”.
      Required.

    - `“angle_offset_is_in_degrees”`: The value (Boolean), if
      true, tells the program to interpret `“angle_offset”` as
      degrees. If false, the program interprets `“angle_offset”` in
      radians. Required.

  - `“EXPLICIT”`: The mode looks for a `“<explicit_index>.txt”` file in the user-created directory
    (`input/<input sample name>/explicit_fibersets`, where `<input sample name>` is the `sample` parameter in
    **_Sample_**) for user-specified fiber (x,y)-coordinates, defined in microns from the *bottom left corner
    of the input images*, (see `config/templates/explicit.txt`). Note, this file is only required if the user
    is using the `“EXPLICIT”` `“FiberXYMode”`. An error is thrown if any explicitly defined coordinates are
    not inside any fascicle inner boundaries.

    - `“explicit_fiberset_index”`: The value (Integer) indicates which explicit index file to use.

  - `“EXPLICIT_3D”`: The mode looks for a `“<explicit_index>.npy”` file in the user-created directory
    (`input/<input sample name>/explicit_fibersets`, where `<input sample name>` is the `sample` parameter
    in **_Sample_**) for user-specified fiber (x,y,z)-coordinates in microns from the left x, bottom y, and
    bottom z coordinates of the input image (see `config/templates/explicit_3D.npy`). Note, this file is
    only required if the user is using the `“EXPLICIT_3D”` `“FiberXYMode”`. The explicit coordinates data
    structure in the pickled `.npy` file must be a numpy array of fibers, where each index contains a 2D
    np.array of fiber xyz-points (e.g., np.array(np.array(fiber 1 xyz-coords), ..., np.array(fiber N
    xyz-coords)). The lengths fibers may be differ. An error is thrown if any explicitly defined coordinates
    are not inside any fascicle inner boundaries. If the fibers are shorter than the length of the model,
    the whole population of the provided fiber coordinates is centered longitudinally by default, and each
    fiber is individually extruded to the length of the model.

    To visualize the `explicit_3D.npy` template, open a command-line window and change directories to
    `config/templates/`. Enter `python` to start an interactive python session and enter
    `import numpy as np`. Then run the `np.load('explicit_3D.npy', allow_pickle=True)` to load and print
    the file contents to the consol. The template file contains two short fibers of varying lengths, and
    is compatible with the ascent tutorial.

    To generate a 3D coordinate file: Create a python list of fibers, where each index is a 2D np.array of
    xyz values. To save a python list of np.arrays of varying lengths to a .npy file, use
    `np.save('<file name>.npy', np.array(<list of fiber arrays>, dtype=object), allow_pickle=True)`.)

    - `“explicit_fiberset_index”`: The value (Integer) indicates which explicit index file to use.

  - `“UNIFORM_DENSITY”`: Place fibers randomly in each inner to
    achieve a consistent number of fibers per unit area.

    - `“top_down”`: The value (Boolean) dictates how the pipeline
      determines how many fibers to seed in each inner. Required.

      - If `“top_down”` is true, the program determines the
        number of fibers per inner with the `“target_density”`.
        If the number of fibers in an inner is less than the
        `“minimum_number”`, then the minimum number is used.

        - `“target_density”`: The value (Double) is the density
          (fibers/µm<sup>2</sup>). Required only if
          `“top_down”` is true.

        - `“minimum_number”`: The value (Integer) is the
          minimum number of fibers that the program will place
          in an inner. Required only if `“top_down”` is true.

      - If `“top_down”` is false (i.e., bottom-up), the program
        determines the number of fibers per unit area (i.e.,
        fiber density) with `“target_number”` and the area of the
        smallest inner. If the number of fibers in an inner is
        more than the `“maximum_number”`, then the maximum number
        is used.

        - `“target_number”`: The value (Integer) is the number
          of fibers placed in the smallest inner. Required
          only if `“top_down”` is false.

        - `“maximum_number”`: The value (Integer) is the
          maximum number of fibers placed in the largest
          inner. Required only if `“top_down”` is false.

    - `“seed”`: The value (Integer) is the seed for the random
      number generator that is instantiated before the point
      picking algorithm for fiber (x,y)-coordinates starts.
      Required.

`“waveform”`: The waveform JSON Object contains key-value pairs to
instruct the system in setting global time discretization settings and
stimulation waveform parameters ([Fig 3C](https://doi.org/10.1371/journal.pcbi.1009285.g003)). Required.

- `“global”`: the value (JSON Object) contains key-value pairs that
  define NEURON time discretization parameters. Required.

  - `“dt”`: The value (Double, units: milliseconds) is the time step
    used in the NEURON simulation for fiber response to electrical
    stimulation. Required.

  - `“on”`: The value (Double, units: milliseconds) is the time when
    the extracellular stimulation is turned on. Required.

  - `“off”`: The value (Double, units: milliseconds) is the time when
    the extracellular stimulation is turned off. Required.

  - `“stop”`: The value (Double, units: milliseconds) is the time when
    the simulation stops. Required.

The user must also provide **_one_** of the
following JSON Objects containing “WaveformMode”-specific parameters.
The user can only loop parameters for one type of waveform in a
**_Sim_**.

```{note}
The “digits” parameter for the following “WaveformModes” sets the
precision of the unscaled current amplitude. For waveforms that are only
ever +/-1 and 0 (e.g., `MONOPHASIC_PULSE_TRAIN`, `BIPHASIC_FULL_DUTY`,
`BIPHASIC_PULSE_TRAIN`), the user can represent the waveform faithfully
with 1 digit of precision. However, for waveforms that assume
intermediate values (e.g., `SINUSOID`,
`BIPHASIC_PULSE_TRAIN_Q_BALANCED_UNEVEN_PW`, `EXPLICIT`) more digits
of precision may be required to achieve numerical accuracy. An excessive
number of digits of precision will increase computational load and waste
storage resources.
```

```{Note}
If one of the parameter values in the `“WaveformMode”` JSON Object
is a list, then there are `n_sim/` folders created for as many waveforms
as parameter values in the list. If more than one parameter value is a
list, then there are `n_sim/` folders created for each combination of
waveform parameters among the lists (i.e., the Cartesian product).
```

- `“MONOPHASIC_PULSE_TRAIN”`

  - `“pulse_width”`: The value (Double, or List\[Double\], units:
    milliseconds) is the duration (“width”) of the monophasic
    rectangular pulse. Required.

  - `“pulse_repetition_freq”`: The value (Double, or List\[Double\],
    units: Hz) is the rate at which individual pulses are delivered.
    Required.

  - `“digits”`: The value (Integer) is the number of digits of
    precision used in saving the waveform to file. Required.

- `“SINUSOID”`

  - `“pulse_repetition_freq”`: The value (Double, or List\[Double\],
    units: Hz) is the frequency of the sinusoid. Required.

  - `“digits”`: The value (Integer) is the number of digits of
    precision used in saving the waveform to file. Required.

- `“BIPHASIC_FULL_DUTY”`: This waveform consists of biphasic symmetric
  rectangular pulses, where there is no “off” time between repetitions
  of the biphasic pulse, hence the “full duty cycle” designation.
  Thus, the phase width (i.e., the duration of one phase in the
  symmetric pulse) is equal to half of the period, as defined by the
  specified `“pulse_repetition_freq”`. This waveform is a special case
  of `“BIPHASIC_PULSE_TRAIN_Q_BALANCED_UNEVEN_PW”` (below).

  - `“pulse_repetition_freq”`: The value (Double, or List\[Double\],
    units: Hz) is the rate at which individual pulses are delivered.
    Required.

  - `“digits”`: The value (Integer) is the number of digits of
    precision used in saving the waveform to file. Required.

- `“BIPHASIC_PULSE_TRAIN”`: This waveform consists of biphasic
  symmetric rectangular pulses, where the phase width (i.e., the
  duration of one phase of the symmetric pulse) is defined by
  `“pulse_width”` and the two phases of the biphasic symmetric pulses
  may be spaced by a gap defined by `“inter_phase”`. This waveform is a
  special case of `“BIPHASIC_PULSE_TRAIN_Q_BALANCED_UNEVEN_PW”`
  (below).

  - `“pulse_width”`: The value (Double, or List\[Double\], units:
    milliseconds) is the duration (“width”) of one phase in the
    biphasic rectangular pulse. Required.

  - `“inter_phase”`: The value (Double, or List\[Double\], units:
    milliseconds) is the duration of time between the first and
    second phases in the biphasic rectangular pulse. Required.

  - `“pulse_repetition_freq”`: The value (Double, or List\[Double\],
    units: Hz) is the rate at which individual pulses are delivered.
    Required.

  - `“digits”`: the value (Integer) is the number of digits of
    precision used in saving the waveform to file. Required.

- `“BIPHASIC_PULSE_TRAIN_Q_BALANCED_UNEVEN_PW”`: This waveform
  consists of biphasic rectangular pulses that are charged-balanced
  (i.e., the charge of the first phase is equal to the charge of the
  second phase), but can be defined to be asymmetrical, such that the
  two phases can have different durations, as defined by
  `“pulse_width_1”` and `“pulse_width_2”`. Further, the two phases
  of the biphasic pulses may be spaced by a gap defined by
  `“inter_phase”`.

  - `“pulse_width_1”`: The value (Double, or List\[Double\], units:
    milliseconds) is the duration (“width”) of the first phase
    (positive amplitude) in the biphasic rectangular pulse.
    Required.

  - `“pulse_width_2”`: The value (Double, or List\[Double\], units:
    milliseconds) is the duration (“width”) of the second phase
    (negative amplitude) in the biphasic rectangular pulse.
    Required.

  - `“inter_phase”`: The value (Double, or List\[Double\], units:
    milliseconds) is the duration of time between the primary and
    secondary phases in the biphasic rectangular pulse (amplitude is
    0). Required.

  - `“pulse_repetition_freq”`: The value (Double, or List\[Double\],
    units: Hz) is the rate at which individual pulses are delivered.
    Required.

  - `“digits”`: The value (Integer) is the number of digits of
    precision used in saving the waveform to file. Required.

- `“EXPLICIT”`

  - `“index”`: The value (Integer) is the index of the explicit
    user-provided waveform stored in
    `config/user/waveforms/<waveform index>.dat` with the time step
    on the first line followed by the current amplitude value
    (unscaled, maximum amplitude +/- 1) at each time step on
    subsequent lines. Required.

  - `“dt_atol”`: The value (Double, units: milliseconds) is the
    tolerance allowed between the time step defined in the explicit
    waveform file and the timestep used in the NEURON simulations
    (see “global” above). If the difference in time step is larger
    than `“dt_atol”`, the user’s explicit waveform is interpolated
    and resampled at the “global” timestep used in NEURON using
    SciPy’s Signal Processing package (`scipy.signal`) \[2\].
    Required.

  - `“period_repeats”`: The number of times (Integer) the input
    signal is repeated between when the stimulation turns “on” and
    “off”. The signal is padded with zeros between simulation
    start (i.e., t=0) and “on”, as well as between “off” and “end”.
    Additionally, the signal is padded with zeros between “on” and
    “off” to accommodate for any extra time after the number of
    period repeats and before “off”. Required.

`“intracellular_stim”`: The value (JSON Object) contains key-value pairs
to define the settings of the monophasic pulse train of the
intracellular stimulus ([NEURON Scripts](../../Code_Hierarchy/NEURON)). Required.

- `“times”`: The key-value pairs define the time durations
  characteristic of the intracellular stimulation. Required.

  - `“pw”`: The value (Double, units: milliseconds) defines the pulse
    duration of the intracellular stimulation. Required.

  - `“IntraStim_PulseTrain_delay”`: The value (Double, units:
    milliseconds) defines the delay from the start of the simulation
    (i.e., t=0) to the onset of the intracellular stimulation.
    Required.

  - `“IntraStim_PulseTrain_dur”`: The value (Double, units:
    milliseconds) defines the duration from the start of the
    simulation (i.e., t=0) to the end of the intracellular
    stimulation. Required.

- `“pulse_repetition_freq”`: The value (Double, units: Hz) defines the
  intracellular stimulation frequency. Required.

- `“amp”`: The value (Double, units: nA) defines the intracellular
  stimulation amplitude. Required.

- `“ind”`: The value (Integer) defines the section index (unmyelinated)
  or node of Ranvier number (myelinated) receiving the intracellular
  stimulation. The number of sections/nodes of Ranvier is indexed from
  0 and starts at the end of the fiber closest to z = 0. Required.

`“saving”`: The value (JSON Object) contains key-value pairs to define
which state variables NEURON will save during its simulations and at
which times/locations ([NEURON Scripts](../../Code_Hierarchy/NEURON)). Required.

- `“aploctime”`: The value (Boolean), if true, instructs the program to
  save, for each fiber node, the last time that an action potential (defined
  by the threshold value in your protocol) passed over that node. Times are
  written in milliseconds from node 0 to node n (the last node). Note that
  passive end nodes will always have a time of 0 (no action potential
  detected.)

- `“space”`:

  - `“vm”`: The value (Boolean), if true, tells the program to save
    the transmembrane potential at all segments (unmyelinated) and
    sections (myelinated) at the time stamps defined in “times” (see
    below). Required.

  - `“gating”`: The value (Boolean), if true, tells the program to
    save channel gating parameters at all segments (unmyelinated)
    and sections (myelinated) at the time values defined in “times”
    (see below). Note: Only implemented for MRG fibers. Required.

  - `“times”`: The value (List\[Double\], units: milliseconds) contains the
    times in the simulation at which to save the values of the state
    variables (i.e., “gating” or “vm”) that the user has selected to
    save for all segments (unmyelinated) and sections (myelinated).
    Required.

- `“time”`:

  - `“vm”`: The value (Boolean), if true, tells the program to save
    the transmembrane potential at each time step at the locations
    defined in “locs” (see below). Required.

  - `“gating”`: The value (Boolean), if true, tells the program to
    save the channel gating parameters at each time step at the
    locations defined in “locs” (see below). Note: Only implemented
    for MRG fibers. Required.

  - `“istim”`: The value (Boolean), if true, tells the program to save
    the applied intracellular stimulation at each time step.
    Required.

  - `“locs”`: The value (List\[Double\] or String, units: none)
    contains the locations (defined as a decimal percentage, e.g.,
    0.1 = 10% along fiber length) at which to save the values of the
    state variables that the user has selected to save for all
    timesteps. Alternatively, the user can use the value “all”
    (String) to prompt the program to save the state variables at
    all segments (unmyelinated) and sections (myelinated). Required.

- `“end_ap_times”`:

  - `“loc_min”`: The value (Double) tells the program at which location to save
    times at which V<sub>m</sub> passes the threshold voltage (defined below)
    with a positive slope. The value must be between 0 and 1, and less than the
    value for `“loc_max”`. Be certain not to record from the end section (i.e., 0)
    if it is passive. A value 0 corresponds to z=0, and a value of 1 corresponds to
    z=length of proximal domain. Required if this JSON object (which is optional) is included.

  - `“loc_max”`: The value (Double) tells the program at which location to save
    times at which V<sub>m</sub> passes the threshold voltage (defined below)
    with a positive slope. The value must be between 0 and 1, and greater than the
    value for `“loc_min”`. Be certain not to record from the end section (i.e., 1)
    if it is passive. A value 0 corresponds to z=0, and a value of 1 corresponds to
    z=length of proximal domain. Required if this JSON object (which is optional) is included.

  - `“threshold”`: The value (Double, units: mV) is the threshold value for V<sub>m</sub> to pass
    for an action potential to be detected. Required if this JSON object (which is optional)
    is included.

- `“runtimes”`: The value (Boolean), if true, tells the program to save
  the NEURON runtime for either the finite amplitude or bisection search for
  threshold simulation. If this key-value pair is omitted, the default
  behavior is False.

- `"3D_fiber_intermediate_data"`: The value (Boolean), if true, tells the program to save the fiber lengths and longitudinal coordinate compartment spacings for sampled potentials into directories within the sample called `tracto_lengths/`, `tracto_coords/`, `3D_tracto_fiberset/` respectively.

- `“cap_recording”`:

  - `“Imembrane_matrix”`: The value (Boolean), if true, tells the program to save the
    transmembrane current matrix for each fiber. These are memory-intensive matrices that contain the transmembrane currents for all fiber compartments across all time points. The matrices are required if the user aims to later generate current templates using the `examples\analysis\generate_templates.py` script. Default: False. Optional.


`“protocol”`:

- `“mode”`: The value (String) is the `“NeuronRunMode”` that tells the
  program to run activation thresholds, block thresholds, or a list of
  extracellular stimulation amplitudes ([NEURON Scripts](../../Code_Hierarchy/NEURON)). Required.

  - As listed in Enums ([Enums](../../Code_Hierarchy/Python.md#enums)), known `“NeuronRunModes”` include

    - `“ACTIVATION_THRESHOLDS”`
    - `“BLOCK_THRESHOLDS”`
    - `“FINITE_AMPLITUDES”`

- `“initSS”`: The value (Double, hint: should be negative or zero,
  units: milliseconds) is the time allowed for the system to reach
  steady state before starting the simulation proper. Required.

- `“dt_initSS”`: The value (Double, units: milliseconds) is the time
  step (usually larger than “dt” in “global” JSON Object (see above))
  used to reach steady state in the NEURON simulations before starting
  the simulation proper. Required.

- `“amplitudes”`: The value (List\[Double\], units: mA) contains
  extracellular current amplitudes to simulate. Required if running
  `“FINITE_AMPLITUDES”` for `“NeuronRunMode”`.

- `“threshold”`: The JSON Object contains key-value pairs to define what
  constitutes threshold being achieved. Required for threshold finding
  protocols (i.e., `“ACTIVATION_THRESHOLDS”` and `“BLOCK_THRESHOLDS”`)
  only. Optional for `"FINITE_AMPLITUDES"` protocol. (In this case, defines the
  threshold for checking if an amplitude activates the fiber being simulated.)

  - `“value”`: The value (Double, units: mV) is the transmembrane
    potential that must be crossed with a rising edge for the NEURON
    code to count an action potential. Required for threshold
    finding protocols (i.e., `“ACTIVATION_THRESHOLDS”` and
    `“BLOCK_THRESHOLDS”`) only. Optional for `"FINITE_AMPLITUDES"` protocol.

  - `“ap_detect_location”`: The value (Double) is the location
    (range 0 to 1, i.e., 0.9 is 90% of the fiber length in the
    +z-direction) where action potentials are detected for threshold
    finding protocols (i.e., `“ACTIVATION_THRESHOLDS”` or
    `“BLOCK_THRESHOLDS”`). Note: If using fiber models with passive
    end nodes, the user should not try to detect action potentials
    at either end of the fiber. Required for threshold finding
    protocols (i.e., `“ACTIVATION_THRESHOLDS”` and
    `“BLOCK_THRESHOLDS”`) only. Optional for `"FINITE_AMPLITUDES"` protocol.

- `“bounds_search”`: the value (JSON Object) contains key-value pairs
  to define how to search for upper and lower bounds in bisection search
  algorithms ([Simulation Protocols](../../Running_ASCENT/Info.md#simulation-protocols)). Required for threshold finding protocols (i.e.,
  `“ACTIVATION_THRESHOLDS”` and `“BLOCK_THRESHOLDS”`).

  - `“mode”`: the value (String) is the `“SearchAmplitudeIncrementMode”`
    that tells the program how to change the initial upper and lower
    bounds for the bisection search; the bounds are adjusted
    iteratively until the initial upper bound (i.e., “top”)
    activates/blocks and until the initial lower bound does not
    activate/block, before starting the bisection search ([Simulation Protocols](../../Running_ASCENT/Info.md#simulation-protocols)). Required.

    - As listed in Enums ([Enums](../../Code_Hierarchy/Python.md#enums)), known `“SearchAmplitudeIncrementModes”`
      include:

      - `“ABSOLUTE_INCREMENT”`: If the current upper bound does
        not activate/block, increase the upper bound by a fixed
        “step” amount (e.g., 0.001 mA). If the lower bound
        activates/blocks, decrease the lower bound by a fixed
        “step” amount (e.g., 0.001 mA).

      - `“PERCENT_INCREMENT”`: If the upper bound does not
        activate/block, increase the upper bound by a “step”
        percentage (e.g., 10 for 10%). If the lower bound
        activates/blocks, decrease the lower bound by a “step”
        percentage (e.g., 10 for 10%).

  - `“top”`: The value (Double, units: mA) is the upper-bound stimulation
    amplitude first tested in a bisection search for thresholds.
    Required.

  - `“bottom”`: The value (Double, units: mA) is the lower-bound stimulation
    amplitude first tested in a bisection search for thresholds.
    Required.

  - `“step”`: The value (Double, units: mA) is the incremental increase/decrease
    of the upper/lower bound in the bisection search. Required.

    - If `“ABSOLUTE_INCREMENT”`, the value (Double, unit: mA) is an
      increment in milliamps.

    - If `“PERCENT_INCREMENT”`, the value (Double, units: %) is a
      percentage (e.g., 10 is 10%).

  - `"max_steps"`: The value (Integer) is the number iterations that will be used in search of a threshold.
    If the program does not find search bounds which encapsulate threshold
    (i.e., one bound activates and the other does not) within this number of iterations, the search protocol will exit.

  - `“scout”`: The value (JSONObject) is a set of key-value pairs specifying a previously run "scout"
    Sim for the same Sample. Use this feature to reduce CPU time required for many
    fibers placed in the same inner for a new Sim or Model. If this key is present, ASCENT will
    look for thresholds in n_sim folders in your ASCENT_NSIM_EXPORT_PATH
    (i.e., the path you set in config/system/env.json) for fiber0 of each
    inner for each n_sim. The program will load this threshold value and use
    it as a starting point for the threshold bounds for each inner in your new Sim.
    The upper- and lower-bounds in the bisection search will be "bounds_search" -> "step" %
    higher and lower, respectively, of the scout Sim's fiber0 threshold. All parameters except
    fiber location (i.e., "fibers" -> "xy_location" in Sim) must match between
    the scout Sim and the current Sim, since the n_sim indices must match between the
    scout Sim and current Sim. If this key ("scout") is present, the program will ignore
    the threshold bounds "top" and "bottom" in "protocol" -> "bounds_search"
    (Unless the specified scout Sim is not found, in which case
    "top" and "bottom" will be used). Optional.

    - `"model"`: The value (Integer) indicates which model index to use for the scout Sim. Required if `"scout"` is used.

    - `"sim"`: The value (Integer) indicates which sim index to use fo the scout Sim (can be the current Sim's index). Required if `"scout"` is used.

<!-- end list -->

- `“termination_criteria”`: Required for threshold finding protocols
  (i.e., `“ACTIVATION_THRESHOLDS”` and `“BLOCK_THRESHOLDS”`) ([Simulation Protocols](../../Running_ASCENT/Info.md#simulation-protocols)).

  - `“mode”`: The value (String) is the `“TerminationCriteriaMode”` that
    tells the program when the upper and lower bound have converged
    on a solution of appropriate precision. Required.

    - As listed in Enums ([Enums](../../Code_Hierarchy/Python.md#enums)), known `“TerminationCriteriaModes”`
      include:

      - `“ABSOLUTE_DIFFERENCE”`: If the upper bound and lower
        bound in the bisection search are within a fixed
        “tolerance” amount (e.g., 0.001 mA), the upper bound
        value is threshold.

        - `“tolerance”`: The value (Double) is the absolute
          difference between upper and lower bound in the
          bisection search for finding threshold (unit: mA).
          Required.

      - `“PERCENT_DIFFERENCE”`: If the upper bound and lower
        bound in the bisection search are within a relative
        “percent” amount (e.g., 1%), the upper bound value is
        threshold. This mode is generally recommended as the
        `ABSOLUTE_DIFFERENCE` approach requires adjustment of the
        “tolerance” to be suitable for different threshold
        magnitudes.

        - `“percent”`: The value (Double) is the percent
          difference between upper and lower bound in the
          bisection search for finding threshold (e.g., 1 is 1%).
          Required.

`“supersampled_bases”`: Optional. Required only for either generating or
reusing super-sampled bases. This can be a memory efficient process by
eliminating the need for long-term storage of the bases/ COMSOL `*.mph`
files. Control of `“supersampled_bases”` belongs in **_Sim_** because the
(x,y)-fiber locations in the nerve are determined by **_Sim_**. The
potentials are sampled densely along the length of the nerve at
(x,y)-fiber locations once so that in a future pipeline run different
fiber types can be simulated at the same location in the nerve cross-section without loading COMSOL files into memory.

- `“generate”`: The value (Boolean) indicates if the program will create
  super-sampled fiber coordinates and super-sampled bases (i.e.,
  sampled potentials from COMSOL). Required only if generating
  `ss_bases/`.

- `“use”`: The value (Boolean) if true directs the program to
  interpolate the super-sampled bases to create the extracellular
  potential inputs for NEURON. If false, the program will sample along
  the length of the COMSOL FEM at the coordinates explicitly required
  by “fibers”. Required only if generating `ss_bases/`.

- `“dz”`: The value (Double, units: micrometer) is the spatial sampling
  of the super-sampled bases. Required only if generating `ss_bases/`.

- `“source_sim”`: The value (Integer) is the **_Sim_** index that
  contains the super-sampled bases. If the user sets both “generate”
  and “use” to true, then the user should indicate the index of the
  current **_Sim_** here. Required only if generating `ss_bases/`.

<!-- end list -->

- `"termination_criteria"`: Required for threshold finding protocols
  (i.e., `"ACTIVATION_THRESHOLDS"` and `"BLOCK_THRESHOLDS"`) ([Simulation Protocols](../../Running_ASCENT/Info.md#simulation-protocols)).

  - `"mode"`: The value (String) is the `"TerminationCriteriaMode"` that
    tells the program when the upper and lower bound have converged
    on a solution of appropriate precision. Required.

    - As listed in Enums ([Enums](../../Code_Hierarchy/Python.md#enums)), known `"TerminationCriteriaModes"`
      include:

      - `"ABSOLUTE_DIFFERENCE"`: If the upper bound and lower
        bound in the bisection search are within a fixed
        "tolerance" amount (e.g., 0.001 mA), the upper bound
        value is threshold.

        - `"tolerance"`: The value (Double) is the absolute
          difference between upper and lower bound in the
          bisection search for finding threshold (unit: mA).
          Required.

      - `"PERCENT_DIFFERENCE"`: If the upper bound and lower
        bound in the bisection search are within a relative
        "percent" amount (e.g., 1%), the upper bound value is
        threshold. This mode is generally recommended as the
        `ABSOLUTE_DIFFERENCE` approach requires adjustment of the
        "tolerance" to be suitable for different threshold
        magnitudes.

        - `"percent"`: The value (Double) is the percent
          difference between upper and lower bound in the
          bisection search for finding threshold (e.g., 1 is 1%).
          Required.

`"supersampled_bases"`: Optional. Required only for either generating or
reusing super-sampled bases. This can be a memory efficient process by
eliminating the need for long-term storage of the bases/ COMSOL `*.mph`
files. Control of `"supersampled_bases"` belongs in **_Sim_** because the
(x,y)-fiber locations in the nerve are determined by **_Sim_**. The
potentials are sampled densely along the length of the nerve at
(x,y)-fiber locations once so that in a future pipeline run different
fiber types can be simulated at the same location in the nerve cross-section without loading COMSOL files into memory.

- `"generate"`: The value (Boolean) indicates if the program will create
  super-sampled fiber coordinates and super-sampled bases (i.e.,
  sampled potentials from COMSOL). Required only if generating
  `ss_bases/`.

- `"use"`: The value (Boolean) if true directs the program to
  interpolate the super-sampled bases to create the extracellular
  potential inputs for NEURON. If false, the program will sample along
  the length of the COMSOL FEM at the coordinates explicitly required
  by "fibers". Required only if generating `ss_bases/`.

- `"dz"`: The value (Double, units: micrometer) is the spatial sampling
  of the super-sampled bases. Required only if generating `ss_bases/`.

- `"source_sim"`: The value (Integer) is the **_Sim_** index that
  contains the super-sampled bases. If the user sets both "generate"
  and "use" to true, then the user should indicate the index of the
  current **_Sim_** here. Required only if generating `ss_bases/`.

<!-- end list -->

## Example

```{eval-rst}
.. include:: ../../../../config/templates/sim.json
   :code: javascript
```
