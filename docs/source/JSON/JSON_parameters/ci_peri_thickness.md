
# ci\_peri\_thickness.json

Named file: `config/system/ci_peri_thickness.json`

## Purpose
The file stores `“PerineuriumThicknessMode”` definitions that
  are referenced in `sample.json` (`“ci_perineurium_thickness”`) for
  assigning perineurium thickness values to fascicles for a mask of
  inners if `“ci_perineurium_thickness”` is not specified as "MEASURED".
  The calculated thickness may be explicitly built in the FEM geometry
  and meshed (i.e., if `“use_ci”` in ***Model*** is false) or may only
  be used for calculating the contact impedance if modeling the
  perineurium with a thin layer approximation ([S14](S14-Creating-sample-specific-nerve-morphologies-in-COMSOL) and [S28](S28-Definition-of-perineurium) Text).

## Syntax
  ```
  {
    "ci_perineurium_thickness_parameters": {
      "GRINBERG_2008": {
        "a": Double,
        "b": Double
      },
      ...
    }
  }
  ```
## Properties

  `“<PerineuriumThicknessMode>”`: JSON Object that contains key-value
  pairs defining the relationship between fascicle diameter (micrometers)
  and perineurium thickness. Required.

    - `“a”`: Value (Double, units: µm/µm) as in thickness = a\*x + b

    - `“b”`: Value (Double, units: µm) as in thickness = a\*x + b

  <!-- end list -->

## Example

  <!-- end list -->

    - See: `config/system/ci_peri_thickness.json` to see all built-in
      `PerineuriumThicknessMode` relationships.
