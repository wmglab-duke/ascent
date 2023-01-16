# env.json

Named file: `config/system/env.json`

## Purpose

The file contains key-value pairs for paths. The file can
be automatically populated by running `env_setup.py` ([Installation](../../Getting_Started.md#installation)). Note that we
have prepended all the keys in this file with "ASCENT" because
these key-value pairs are directly stored as environment variables,
so the "ASCENT" key distinguishes these pairs from other paths that
may be present on your computer.

## Syntax

To declare this entity in `config/system/env.json`, use the
following syntax:

```javascript
{
  "ASCENT_COMSOL_PATH": String,
  "ASCENT_JDK_PATH": String,
  "ASCENT_PROJECT_PATH": String,
  "ASCENT_NSIM_EXPORT_PATH": String
}
```

## Properties

`"ASCENT_COMSOL_PATH"`: The value (String) is the path for your local
COMSOL installation.
`"ASCENT_JDK_PATH"`: The value (String) is the path for your local Java
JDK installation.
`"ASCENT_PROJECT_PATH"`: The value (String) is the path for your local
ASCENT repository.
`"ASCENT_NSIM_EXPORT_PATH"`: The value (String) is the path where the
pipeline will save NEURON simulation directories to submit.

## Example

<!-- end list -->

````{tab} macOS and Linux
```{eval-rst}
.. include:: ../../../../config/templates/unix_env.json
   :code: javascript
```
````

````{tab} Windows
```{eval-rst}
.. include:: ../../../../config/templates/windows_env.json
   :code: javascript
```
````
