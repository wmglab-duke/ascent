# materials.json

Named file: `config/system/materials.json`

## Purpose

Stores default material and tissue properties in the
pipeline for use in the 3D FEM.

## Syntax

To declare this entity in `config/system/materials.json`, use
the following syntax:

```javascript
{
  "conductivities": {
    "endoneurium": { // example syntax for anisotropic medium
      "value": "anisotropic",
      "sigma_x": String,
      "sigma_y": String,
      "sigma_z": String,
      "unit": "String",
      "references": {
        "1": String,
        ...,
        "n": String
      }
    },
    "epineurium": { // example syntax for isotropic medium
      "value": "String",
      "unit": "String",
      "references": {
        "1": String,
        ...,
        "n": String
      }
    }
  }
}
```

## Properties

`"<material>"`: The value is a JSON Object containing the conductivity
value and units as Strings. Though using strings may seem odd for
storing conductivity values, we do this because we read them directly
into COMSOL to define materials, and COMSOL expects a string (which it
evaluates as expression).

- `"value"`: The conductivity of the material (if not "anisotropic", the
  value must be in units S/m). If the value is "anisotropic", the
  system is expecting additional keys for the values in each Cartesian
  direction:

  - `"sigma_x"`: The value (String) is the conductivity in the
    x-direction (unit: S/m)

  - `"sigma_y"`: The value (String) is the conductivity in the
    y-direction (unit: S/m)

  - `"sigma\_z"`:  The value (String) is the conductivity in the
    z-direction (unit: S/m)

- `"unit"`: The unit of the associated conductivity in square brackets
  (must be "\[S/m\]")

- `"references"`: The value (Dictionary) contains citations to the source of the material conductivity used. The contents are non-functional (i.e., they are not used in any of the code), but they serve as a point of information reference for good bookkeeping. Each reference used is assigned its own key-value pair (Optional).

<!-- end list -->

## Example

<!-- end list -->

See: `config/system/materials.json` to see all built-in material
definitions, which the user may add to.

Note: Perineurium can be represented in the pipeline as either a meshed
domain with a finite thickness or as a thin layer approximation, but the
conductivity value used for either method is defined in `materials.json`
unless the `"PerineuriumResistivityMode"` is `"MANUAL"` and the conductivity
is defined explicitly in **_Model_** ([Perineurium Properties](../../Running_ASCENT/Info.md#definition-of-perineurium)).
