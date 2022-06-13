# run.json

Named file: `config/user/runs/<run_index>.json`

## Purpose
Instructs the pipeline on which input data and user-defined
parameters to use in a single program "run", where one "run"
configuration serves a single ***Sample*** and a list of
***Model(s)*** and ***Sims(s)***. Enables operational control
(breakpoints, which FEM files to save/discard). Keeps track of
successful/failed FEMs in Java.

## Syntax
To declare this entity in `config/user/runs/`, use the
following syntax:
```
{
  "submission_context": String,
  "sample": Integer, // note, only one value here!
  "models": [Integer, ...], // pipeline will create all pairwise combos of …
  "sims": [Integer, ...], // … models and sims
  "recycle_meshes": Boolean,
  "break_points": {
    "pre_java": Boolean, // before Runner’s handoff() method to Java/COMSOL
    "pre_geom_run": Boolean, // immediately before geometry operations
    "post_geom_run": Boolean, // immediately after geometry operations
    "pre_mesh_proximal": Boolean, // immediately before mesh prox operations
    "post_mesh_proximal": Boolean, // immediately post mesh prox operations
    "pre_mesh_distal": Boolean, // immediately before mesh dist operations
    "post_mesh_distal": Boolean, // immediately post mesh dist operations
    "post_material_assign": Boolean, // immediately post assigning materials
    "pre_loop_currents": Boolean // immediately before solving for bases
  },
  "models_exit_status": [Boolean, ...], // one entry for each Model
  "keep": {
    "debug_geom": Boolean,
    "mesh": Boolean,
    "bases": Boolean
  },
  "partial_fem": {
    "cuff_only": Boolean,
    "nerve_only": Boolean
  },
  "local_avail_cpus": Integer,
  "override_compiled_mods": Boolean
}
```
## Properties

`"submission_context"`: The value (String) of this property tells the
system how to submit the n\_sim NEURON jobs based on the computational
resources available. Value can be "cluster", "local", or "auto" (if "auto", "hostname_prefix" is required). Required.

`"hostname_prefix"`: This value (String) tells the program what prefix to look out for in the "HOSTNAME" environment variable. If the "HOSTNAME" begins with the "hostname prefix", submission context is set to cluster, otherwise it is set to local (does not change the value in the configuration file). Example: if your high performance computing cluster hostname always begins with ourclust, e.g. ourclust-node-15, ourclust-login-20, etc., you would set the value of this variable to "ourclust." If the "HOSTNAME" environment variable is not present, the program defaults to "local." Required if "submission_context" is "auto", otherwise Optional.

`"sample"`: The value (Integer) of this property sets the sample
configuration index ("***Sample***"). Note that this is only ever one
value. To loop ***Samples***, create a ***Run*** for each. Required.

`"models"`: The value (\[Integer, ...\]) of this property sets the model
configuration indices ("***Model***"). Required.

`"sims"`:  The value (\[Integer, ...\]) of this property sets the
simulation configuration indices ("***Sim***"). Required.

`"recycle_meshes"`: The value (Boolean) of this property instructs the
pipeline to search for mesh matches for recycling a previously generated
FEM mesh if set to true. If this property is not specified, the default
behavior of the pipeline is false, meaning that it will not search for
and recycle a mesh match (see `ModelSearcher` ([S26 Text](S26-Java-utility-classes)) and
`mesh_dependent_model.json` ([S7 Text](S7-JSON-configuration-files))). Optional.

`"break_points"`: The value (Boolean) of each breakpoint results in the
program terminating or continuing with the next ***Model*** index. In
Runner, the program checks that at most one breakpoint is true and
throws an exception otherwise. The breakpoint locations enable the user
to run only up to certain steps of the pipeline, which can be
particularly useful for debugging. If a breakpoint is not defined, the
default behavior is false (i.e., the pipeline continues beyond the
breakpoint). Note: specifying a break point via command line arguments
will override any break points set in your run config. Optional.

`"models_exit_status"`: The value (\[Boolean, ...\]) of this property
indicates if Java successfully made the FEMs for the corresponding model
indices ("models" property). The user does not need to include this
property before performing a run of the pipeline, as it is automatically
added in Java (COMSOL FEM processes) and is then used to inform Python
operations for making NEURON simulations. The value will contain one
value for each ***Model*** listed in "models". If a ***Model*** fails,
the pipeline will skip it and proceed to the next one. Automatically
added.

`"keep"`: The value (Boolean) of each property results in the program
keeping or deleting large COMSOL `*.mph` files for the `"debug_geom.mph"`,
`"mesh.mph"` and bases/ for a given ***Model***. If a keep property is not
defined, the default behavior is true and the associated `*.mph` file is
saved. If `"mesh.mph"` is saved, the file can later be used if another
***Model*** is a suitable "mesh match" and `"recycle_meshes"` is true
(see `ModelSearcher` ([S26 Text](S26-Java-utility-classes)) and `mesh_dependent_model.json` ([S7 Text](S7-JSON-configuration-files))). If bases/ are saved, a
new ***Sim*** for a previously computed ***Sample*** and ***Model*** can
be probed along new fibersets/ to create potentials/*.* Optional.

`"partial_fem"`: The value (Boolean) of each property results in the
program terminating after building the COMSOL FEM geometry for only the
cuff (`"cuff_only"`) or only the nerve (`"nerve_only"`). The program
terminates after the `"debug_geom.mph"` file is created. If the
`"partial_fem"` JSON Object is not included, the value of each Boolean
is treated as false, meaning that the `"debug_geom.mph"` file will
contain the nerve and cuff electrode. An error is thrown if the user may
set both values for `"cuff_only"` and `"nerve_only"` to true. To build the
geometry of both the cuff and the nerve, but not proceed with meshing or
solving the FEM, the user should set the value for `"post_geom_run"`
under `"break_points"` to true. Overriden
if the `"partial_fem"` command line argument is used. Optional.

`"local_avail_cpus"`: The value (Integer) sets the number of CPUs that
the program will take if the `"submission_context"` is "local". We check
that the user is not asking for more than one less that the number of
CPUs of their machine, such that at least one CPU is left for the
machine to perform other processes. Optional, but if using submitting
locally, the program will take all CPUs except 1 if this value is not
defined.

`"override_compiled_mods"`: The value (Boolean) indicates if the program will override previously compiled *.mod files (i.e. files defining channel mechanisms in NEURON) with each system call of submit.py. Optional, but if the key is omitted the program will not override previously compiled *.mod files.

## Example
```
{
  "submission_context": "cluster",
  "sample": 62,
  "models": [0],
  "sims": [99],
  "recycle_meshes": true,
  "break_points": {
    "pre_java": false,
    "pre_geom_run": false,
    "post_geom_run": true,
    "pre_mesh_proximal": false,
    "post_mesh_proximal": false,
    "pre_mesh_distal": false,
    "post_mesh_distal": false,
    "post_material_assign": false,  
    "pre_loop_currents": false
  },
  "models_exit_status": [true],
  "keep": {
    "debug_geom": true,
    "mesh": true,
    "bases": true
  },
  "partial_fem": {
    "cuff_only": false,
    "nerve_only": false
  },
  "local_avail_cpus": 3,
  "override_compiled_mods": false
}
```
