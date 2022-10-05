# run.json

Named file: `config/user/runs/<run_index>.json`

## Purpose

Instructs the pipeline on which input data and user-defined
parameters to use in a single program "run", where one "run"
configuration serves a single **_Sample_** and a list of
**_Model(s)_** and **_Sims(s)_**. Enables operational control
(breakpoints, which FEM files to save/discard). Keeps track of
successful/failed FEMs in Java.

## Syntax

To declare this entity in `config/user/runs/`, use the
following syntax:

```javascript
{
  "pseudonym": String,
  "sample": Integer, // note, only one value here!
  "models": [Integer, ...], // pipeline will create all pairwise combos of …
  "sims": [Integer, ...], // … models and sims
  "recycle_meshes": Boolean,
  "models_exit_status": [Boolean, ...], // one entry for each Model
  "endo_only_solution": Boolean,
  "keep": {
    "debug_geom": Boolean,
    "mesh": Boolean,
    "bases": Boolean
  },
  "export_behavior": String,
  "popup_plots": Boolean,
  "auto_submit_fibers": Boolean
}
```

## Properties

`"pseudonym"`: This value (String) informs pipeline print statements, allowing
users to better keep track of the purpose of each configuration file. Optional.

`"sample"`: The value (Integer) of this property sets the sample
configuration index ("**_Sample_**"). Note that this is only ever one
value. To loop **_Samples_**, create a **_Run_** for each. Required.

`"models"`: The value (\[Integer, ...\]) of this property sets the model
configuration indices ("**_Model_**"). Required.

`"sims"`:  The value (\[Integer, ...\]) of this property sets the
simulation configuration indices ("**_Sim_**"). Required.

`"recycle_meshes"`: The value (Boolean) of this property instructs the
pipeline to search for mesh matches for recycling a previously generated
FEM mesh if set to true. If this property is not specified, the default
behavior of the pipeline is false, meaning that it will not search for
and recycle a mesh match (see `ModelSearcher` ([Java Utility Classes](../../Code_Hierarchy/Java.md#java-utility-classes)) and
`mesh_dependent_model.json` ([Mesh Dependent Model](../../JSON/JSON_parameters/mesh_dependent_model))). Optional.

`"endo_only_solution"`: The value (Boolean) determines what data the electric currents
solution will save. Since fibers are sampled from the endoneurium, after the
solution is completed, only the endoneurial Ve data is necessary to run fiber
simulations. If `"endo_only_solution"` is `true`, then COMSOL will save ONLY
the Ve data for the endoneurium. If `false`, COMSOL will save Ve data for the entire model.
Recommended value is `true` unless you intend to generate plots or other analyses
which require Ve data for geometry other than the endoneurium. If this key-value pair
is not present, defaults to `false`. This parameter only affects storage
space after the solution has completed, and will not have any effect on memory
usage or solution time.

`"models_exit_status"`: The value (\[Boolean, ...\]) of this property
indicates if Java successfully made the FEMs for the corresponding model
indices ("models" property). The user does not need to include this
property before performing a run of the pipeline, as it is automatically
added in Java (COMSOL FEM processes) and is then used to inform Python
operations for making NEURON simulations. The value will contain one
value for each **_Model_** listed in "models". If a **_Model_** fails,
the pipeline will skip it and proceed to the next one. Automatically
added.

`"keep"`: The value (Boolean) of each property results in the program
keeping or deleting large COMSOL `*.mph` files for the `"debug_geom.mph"`,
`"mesh.mph"` and bases/ for a given **_Model_**. If a keep property is not
defined, the default behavior is true and the associated `*.mph` file is
saved. If `"mesh.mph"` is saved, the file can later be used if another
**_Model_** is a suitable "mesh match" and `"recycle_meshes"` is true
(see `ModelSearcher` ([Java Utility Classes](../../Code_Hierarchy/Java.md#java-utility-classes)) and `mesh_dependent_model.json` ([Mesh Dependent Model](../../JSON/JSON_parameters/mesh_dependent_model))). If bases/ are saved, a
new **_Sim_** for a previously computed **_Sample_** and **_Model_** can
be probed along new fibersets/ to create potentials/_._ Optional.

`"export_behavior"`: The value (String) instructs the pipeline how to behave if
an export n_sim directory (i.e., ASCENT_NSIM_EXPORT_PATH/n_sims/<directory>)
already exists. There are three options: `"selective"` is the default behavior,
output directories which already exist will be skipped, but any which do not exist
will be generated, `"overwrite"` will remove the extant directory,
and generate a new clean output directory in its place, `"error"` instructs the
pipeline to exit if any export n_sim directory is found to already exist.

`“popup_plots”`: The value (Boolean) will instruct the pipeline to display plots
(e.g. sample plot, fiberset plot, waveform plot) in a popup window. This is in addition
to saving the plots in the relevant folders (i.e., the sample and sim folders).

`"auto_submit_fibers"`: The value (Boolean), if true, will cause the program to automatically start fiber simulations after each run is completed.
If submitting locally, the program will not continue to the next run until all fiber simulations are complete. If submitting via a computer cluster,
the next run will start after all batch NEURON jobs are submitted.

## Example

```{eval-rst}
.. include:: ../../../../config/templates/run.json
   :code: javascript
```
