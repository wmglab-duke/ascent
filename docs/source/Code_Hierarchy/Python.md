# Python Classes
## Python simulation class
###  (Pre-Java)

The user is unlikely to interface directly with Simulation’s
`resolve_factors()` method as it operates behind the scenes. The method
searches through ***Sim*** for lists of parameters within the “fibers”
and “waveform” JSON Objects until the indicated number of dimensions
(“n_dimensions” parameter in ***Sim***, which is a handshake to
prevent erroneous generation of NEURON simulations) has been reached.
The parameters over which the user has indicated to sweep in ***Sim***
are saved to the Simulation class as a dictionary named “factors” with
the path to each parameter in ***Sim***.

The required parameters to define each type of waveform are in [S8 Text](S8-JSON-file-parameter-guide). The Python Waveform class is configured with ***Sim***, which contains
all parameters that define the Waveform. Since FEMs may have
frequency-dependent conductivities, the parameter for frequency of
stimulation is optionally defined in ***Model*** (for frequency-dependent
material conductivities), but the pulse repetition frequency is
defined in ***Sim*** as `“pulse_repetition_freq”`. The
`write_waveforms()` method instantiates a Python Waveform class for each
`“wave_set”` (i.e., one combination of stimulation parameters).

###  (Post-Java)

The unique combinations of ***Sim*** parameters are found with a
Cartesian product from the listed values for individual parameters in
***Sim***: Waveforms ⨉ Src_weights ⨉ Fibersets. The pipeline manages
the indexing of simulations. For ease of debugging and inspection, into
each `n_sim/` directory we copy in a modified “reduced” version of
***Sim*** with any lists of parameters replaced by the single list
element value investigated in the particular `n_sim/` directory.

The Simulation class loops over ***Model*** and ***Sim*** as listed in
***Run*** and loads the Python `“sim.obj”` object saved in each simulation
directory `(sims/\<sim index\>/)` prior to Python’s `handoff()` to Java.
Using the Python object for the simulation loaded into memory, the
Simulation class’s method `build_n_sims()` loops over the
`master_product_index` (i.e., waveforms ⨉ (src_weights ⨉ fibersets)).
For each `master_product_index`, the program creates the `n_sim` file
structure (```sims/<sim index>/n_sims/<n_sim index>/data/inputs/``` and
```sims/<sim index>/n_sims/<n_sim index>/data/outputs/```).
Corresponding to the `n_sim’s` `master_product_index`, files are copied
into the `n_sim` directory for a “reduced” ***Sim***, stimulation
waveform, and fiber potentials. Additionally, the program writes a HOC
file (i.e., `“launch.hoc”`) containing parameters for and a call to our
`Wrapper.hoc` file using the Python `HocWriter` class.

To conveniently submit the `n\_sim` directories to a computer cluster, we
created methods within Simulation named `export_n_sims()`,
`export_run()`, and `export_neuron_files()`. The method `export_n_sims()`
copies `n_sims` from our native hierarchical file structure to a target
directory as defined in the system `env.json` config file by the value for
the `“ASCENT_NSIM_EXPORT_PATH”` key. Within the target directory, a
directory named `n_sims/` contains all `n_sims`. Each `n_sim` is renamed
corresponding to its sample, model, sim, and `master_product_index`
(`<sample_index>_<model_index>_<sim_index>_<master_product_index>`)
and is therefore unique. Analogously, `export_run()` creates a copy of
***Run*** within the target directory in a directory named `runs/`. Lastly,
`export_neuron_files()` is used to create a copy of the NEURON `*.hoc`
and `*.mod` files in the target directory in directories named
`“HOC_Files”` and `“MOD_Files”`, respectively.

## Python utility classes

### Enums
In the Python portions of the pipeline we use
[Enums](https://docs.python.org/3/library/enum.html)
which are “… a set of
symbolic names (members) bound to unique, constant values. Within an
enumeration, the members can be compared by identity, and the
enumeration itself can be iterated over.” Enums improve code readability
and are useful when a parameter can only assume one value from a set of
possible values.

We store our Enums in `src/utils/enums.py`. While programming in Python,
Enums are used to make interfacing with our JSON parameter input and
storage files easier. We recommend that as users expand upon ASCENT’s
functionality that they continue to use Enums, adding to existing
classes or creating new classes when appropriate.


###  Configurable

Configurable is inherited by other Python classes in the ASCENT pipeline
to grant access to parameter and data configuration JSON files loaded to
memory. Configurable has built-in exceptions that it throws which are
indexed negatively (-1 and below by convention) because it is
intrinsically unable to inherit from Exceptionable (errors indexed +1
and above by convention), which, in turn, (Exceptionable) is configured
by inheriting the Configurable class.

Configurable is an important class for developers to understand because
it is the mechanism by which instances of our Python classes inherit
their properties from JSON configuration files (e.g., `sample.json`,
`model.json`, `sim.json`, `fiber_z.json`). The Configurable class takes three
input parameters:

#### `"SetupMode"` (from Enums, [S6 Text](S6-Enums))

Either NEW or OLD which determines if Configurable loads a new JSON
(from file) or uses data that has already been created in Python memory
as a dictionary or list, respectively.

#### ConfigKey (from Enums, [S6 Text](S6-Enums))

The ConfigKey indicates the choice of configuration data type and is
also the name of the configuration JSON file (e.g., `sample.json`,
`model.json`, `sim.json`, `run.json`, `env.json`).

#### Config:

The Config input to Configurable can take one of three data types. If
`“SetupMode”` is “OLD”, the value can be a dictionary or list of already
loaded configuration data. If `“SetupMode”` is “NEW”, the value must be a
string of the file path to the configuration file to be loaded into
memory.

####  Example use of Configurable:

When the Sample class is instantiated in Runner, it inherits
functionality from Configurable (see Sample constructor
`__init__(self, exception_config: list)` in `src/core/sample.py`).

After the Sample class is instantiated, the ***Sample*** configuration
(index indicated in ***Run***) is added to the Sample class with:

`sample.add(SetupMode.OLD, Config.SAMPLE, all_configs[Config.SAMPLE.value][0])`

With the ***Sample*** configuration available to the Sample class, the
class can access the contents of the JSON dictionary. For example, in
`populate()`, the Sample class gets the length of the scale bar from
***Sample*** with the following line:

`self.search(Config.SAMPLE, ‘scale’, ‘scale_bar_length’)`

###  Exceptionable

Exceptionable is a centralized way to organize and throw exceptions
(errors) to the user’s console. Exceptionable inherits functionality
from Configurable. Exceptionable, like Configurable, is initialized with
“SetupMode”, ConfigKey, and a Config. However, the data contents for
Exceptionable are specifically a list of exceptions stored in
`config/system/exceptions.json`. The contents of the exceptions
configuration file is a list of numbered errors with an associated text
description. These contents, along with the path of the script which called
exceptionable, are listed in the event of a raised exception.

###  Saveable

Saveable is a simple Python class that, when inherited by a Python class
(e.g., Sample and Simulation, described in [S13](S13-Python-classes-for-representing-nerve-morphology-(Sample)) and [S30](S30-Python-simulation-class) Text, respectively) enables the class to save itself using
Saveable’s `save()` method. Using `pickle.dump()`, the object is saved as a
Python object to file at the location of the destination path, which is
an input parameter to `save()`.
