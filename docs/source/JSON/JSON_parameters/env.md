
# env.json

Named file: `config/system/env.json`

## Purpose
The file contains key-value pairs for paths. The file can
be automatically populated by running `env_setup.py` ([S2 Text](S2-Installation)). Note that we
have prepended all of the keys in this file with “ASCENT” because
these key-value pairs are directly stored as environment variables,
so the “ASCENT” key distinguishes these pairs from other paths that
may be present on your computer.

## Syntax
To declare this entity in `config/system/env.json`, use the
following syntax:
```
{
  "ASCENT_COMSOL_PATH": String,
  "ASCENT_JDK_PATH": String,
  "ASCENT_PROJECT_PATH": String,
  "ASCENT_NSIM_EXPORT_PATH": String
}
```
## Properties

`“ASCENT_COMSOL_PATH”`: The value (String) is the path for your local
COMSOL installation.
`“ASCENT_JDK_PATH”`: The value (String) is the path for your local Java
JDK installation.
`“ASCENT_PROJECT_PATH”`: The value (String) is the path for your local
ASCENT repository.
`“ASCENT_NSIM_EXPORT_PATH”`: The value (String) is the path where the
pipeline will save NEURON simulation directories to submit.

## Example

<!-- end list -->

  - Windows:
```
{
  "ASCENT_COMSOL_PATH": "C:\\Program Files\\COMSOL\\COMSOL55\\Multiphysics",
  "ASCENT_JDK_PATH": "C:\\Program Files\\Java\\jdk1.8.0_221\\bin",
  "ASCENT_PROJECT_PATH": "D:\\Documents\\ascent",
  "ASCENT_NSIM_EXPORT_PATH": "D:\\Documents\\ascent\\submit"
}
```
  - MacOS
```
{
  "ASCENT_COMSOL_PATH": "/Applications/COMSOL55/Multiphysics ",
  "ASCENT_JDK_PATH":
  "/Library/Java/JavaVirtualMachines/jdk1.8.0_221.jdk/Contents/Home/bin/",
  "ASCENT_PROJECT_PATH": "/Users/ericmusselman/Documents/ascent",
  "ASCENT_NSIM_EXPORT_PATH": "/Users/ericmusselman/Documents/ascent/submit"
}
```
