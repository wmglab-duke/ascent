# mesh_dependent_model.json

Named file: `config/system/mesh_dependent_model.json`

## Purpose

This file is not to be changed unless a user adds new
parameters to **_Model_**. The use of this file happens behind the
scenes. The file informs the `ModelSearcher` class ([Java Utility Classes](../../Code_Hierarchy/Java.md#java-utility-classes)) if two model
configurations constitute a "mesh match" (i.e., that the mesh from a
previously solved and identical model can be recycled). Note that if
you modify the structure of `model.json`, the pipeline expects this
file’s structure to be changed as well. If the Boolean for a
parameter is true, then the parameter values between two
**_Models_** must be identical to constitute a "mesh match". If the Boolean for a parameter is
false, then the parameter values between the two **_Models_** can be
different and still constitute a "mesh match". The process of
identifying "mesh matches" is automated and is only performed if the
`"recycle_meshes"` parameter in **_Run_** is true.

## Syntax

To declare this entity in
`config/system/mesh_dependent_model.json`, use the following syntax:

<!-- end list -->

- The same key-value structure pair as in **_Model_**, but the values
  are of type Boolean

  - true: The parameter values between the two **_Model_**
    configurations must be identical to constitute a "mesh match".

  - false: The parameter values between the two **_Model_**
    configurations can be different and still constitute a "mesh match".

<!-- end list -->

## Properties

See: `model.json`

## Example

See: `config/system/mesh_dependent_model.json`

```{note}
The user should not need to change this file unless adding new
parameters to **_Model_** for expanded/modified pipeline
functionality.
```
