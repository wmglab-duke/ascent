# Data Hierarchy

Each execution of the ASCENT pipeline requires a **_Run_** JavaScript
Object Notation (JSON) configuration file (`<run_index>.json`) that
contains indices for a user-defined set of JSON files. Specifically, a
JSON file is defined for each hierarchical domain of information: (1)
**_Sample_**: for processing segmented two-dimensional transverse
cross-sectional geometry of a nerve sample, (2) **_Model_** (COMSOL
parameters): for defining and solving three-dimensional FEM, including
geometry of nerve, cuff, and medium, spatial discretization (i.e.,
mesh), materials, boundary conditions, and physics, and (3) **_Sim_**
(NEURON parameters): for defining fiber models, stimulation waveforms,
amplitudes, and durations, intracellular test pulses (for example, when
seeking to determine block thresholds), parameters for the binary search
protocol and termination criteria for thresholds, and flags to save
state variables. These configurations are organized hierarchically such
that **_Sample_** does not depend on **_Model_** or **_Sim_**, and
**_Model_** does not depend on **_Sim_**; thus, changes in **_Sim_** do
not require changes in **_Model_** or **_Sample_**, and changes in
**_Model_** do not require changes in **_Sample_** (Figure A).

![Inline image](uploads/e675a31c0bf2bda687c6d696fa145c0c/Picture15.jpg)

Figure A. ASCENT pipeline file structure in the context of Sample (blue), Model (green), and Sim (purple) configurations. [JSON Overview](JSON/JSON_overview) describes the JSON configuration files an their contents, and [JSON Parameters](JSON/JSON_parameters/index) details the syntax and data types of the key-value parameter pairs.

## Batching and sweeping of parameters

ASCENT enables the user to batch rapidly simulations to sweep cuff
electrode placement on the nerve, material properties, stimulation
parameters, and fiber types. The first process of ASCENT prepares
ready-to-submit NEURON simulations to model response of fibers to
extracellular stimulation. The second process of ASCENT uses Python to
batch NEURON jobs to a personal computer or compute cluster to simulate
fiber response to extracellular stimulation. Each task submitted to a
CPU simulates the response of a single fiber to either a set of finite
amplitudes or a binary search for threshold of activation or block,
therefore creating an "embarrassingly parallel" workload.

Groups of fibers from the same **_Sample_**, **_Model_**, **_Sim_**,
waveform, contact weight (i.e., `"src_weights"` in **_Sim_**), and
fiberset (i.e., a group of fibers with the same geometry and channels
and occupy different (x,y)-locations in the nerve cross section) are
organized in the same `n_sim/` directory.

A **_Run_** creates simulations for a single **_Sample_** and all pairs
of listed **_Model(s)_** and **_Sim(s)_**. A user can pass a list of
**_Run_** configurations in a single system call with `"python run pipeline <run_indices>"` to simulate multiple **_Sample_**
configurations in the same system call.

**_Sample_** and **_Model_** cannot take lists of parameters. Rather, if
the user would like to assess the impact of ranges of parameters for
**_Sample_** or **_Model_**, they must create additional **_Sample_**
and **_Model_** configuration files for each parameter value.

**_Sim_** can contain lists of parameters in `"active_srcs"` (i.e., cuff
electrode contact weightings), `"fibers"`, `"waveform"`, and
`"supersampled_bases"`.
