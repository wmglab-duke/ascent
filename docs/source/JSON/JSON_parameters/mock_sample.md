# mock_sample.json

Named file: `config/user/<mock_sample_index>.json`

## Purpose

Instructs the pipeline on which user-defined parameters to
use for synthesizing nerve sample morphology inputs (i.e., 2D binary
images of segmented nerve morphology) for a single sample in
preparation for 3D representation of the nerve in the FEM.

## Syntax

To declare this entity in
config/user/<mock_sample_index>.json, use the following syntax:

```{note}
Eccentricity ($e$) is defined as a function of the major ($a$) and minor ($b$) axes as follows: $e=\sqrt{1-\frac{b^{2}}{a^{2}}}$
```

```javascript
{
  "global": {
    "NAME": String
  },
  "scalebar_length": Double,
  "nerve": {
    "a": Double,
    "b": Double,
    "rot": Double
  },
  "figure": {
    "fig_margin": Double,
    "fig_dpi": Integer
  },

  // EXAMPLE POPULATE Parameters for EXPLICIT
  "populate": {
    "mode": "EXPLICIT",
    "min_fascicle_separation": 5,
    "Fascicles": [
      {
        "centroid_x": Double,
        "centroid_y": Double,
        "a": Double,
        "b": Double,
        "rot": Double
      },
      ...
    ]
  },

  // EXAMPLE POPULATE Parameters for TRUNCNORM
  "populate": {
    "mode": "TRUNCNORM",
    "mu_fasc_diam": Double,
    "std_fasc_diam": Double,
    "n_std_diam_limit": Double,
    "num_fascicle_attempt": Integer,
    "num_fascicle_placed": Integer,
    "mu_fasc_ecc": Double,
    "std_fasc_ecc": Double,
    "n_std_ecc_limit": Double,
    "max_attempt_iter": Integer,
    "min_fascicle_separation": Double,
    "seed": Integer
  },

  // EXAMPLE POPULATE Parameters for UNIFORM
  "populate": {
    "mode": "UNIFORM",
    "lower_fasc_diam": Double,
    "upper_fasc_diam": Double,
    "num_fascicle_attempt": Integer,
    "num_fascicle_placed": Integer,
    "lower_fasc_ecc": Double,
    "upper_fasc_ecc": Double,
    "max_attempt_iter": Integer,
    "min_fascicle_separation": Double,
    "seed": Integer
  }
}
```

## Properties

`"global"`: The global JSON Object contains key-value pairs to document
characteristics of the sample being synthesized. Required.

- `"NAME"`: The value (String) of this property sets the sample
  name/identifier (e.g., Pig1-1) to relate to bookkeeping. The value
  will match the directory name in input/ containing the synthesized
  morphology files created by the `mock_morphology_generator.py`.
  Required.

`"scalebar_length"`: The value (Double, units: micrometer) is the desired
length of the scale bar in the generated binary image of the scale bar
(`s.tif`). Required.

`"nerve"`: The nerve JSON Object contains key-value pairs for the
elliptical nerve’s size and rotation. Required.

- `"a"`: Value is the nerve ellipse axis ‘a’ which is the full width major axis (Double, units:
  micrometer). Required.

- `"b"`: Value is the nerve ellipse axis ‘b’ which is the full width minor axis (Double, units:
  micrometer). Required.

- `"rot_nerve"`: Value is the nerve ellipse axis rotation (Double,
  units: degrees). Positive angles are counter-clockwise and negative
  are clockwise, relative to orientation with a-axis aligned with
  +x-direction. Required.

"figure": The figure JSON Object contains key-value pairs for parameters
that determine the size and resolution of the generated binary masks.
Required.

- `"fig_margin"`: The value (Double, \>1 otherwise an error is thrown)
  sets the x- and y-limits of the binary masks generated. The limits
  are set relative to the maximum nerve ellipse axis dimension (+/-
  `fig_margin`*max(`a`, `b`) in both x- and y-directions).
  Required.

- `"fig_dpi"`: The value (Integer) is the "dots per inch" resolution of
  the synthesized binary images. Higher resolutions will result in
  more accurate interpolation curves of inners in COMSOL. We recommend
  \>1000 for this value. Required.

`"populate"`: The populate JSON Object contains key-value pairs for
parameters that determine how the nerve contents (i.e., fascicle inners)
are populated. Required.

- `"mode"`: The value (String) is the `"PopulateMode"` that tells the
  program which method to use to populate the nerve. Required.

  - As listed in Enums ([Enums](../../Code_Hierarchy/Python.md#enums)), known `"PopulateModes"` include

    - `"EXPLICIT"`: Populates the nerve with elliptical inners that
      are defined explicitly by the user.

      - `"min_fascicle_separation"`: The value (Double, units:
        micrometer) determines the minimum distance between
        fascicle boundaries in the binary mask image that the
        pipeline will allow without throwing an error. This
        value controls the separation required between fascicles
        in the binary mask only. There is a separate parameter
        for forcing a distance (post-deformation) of the nerve
        between fascicles and between fascicles and the nerve
        boundary in `sample.json`. Required.

      - `"Fascicles"`: The value `List[JSON Object]` contains a
        JSON Object for each inner. Required. Within each JSON
        Object, the following key-value pairs are present:

        - `"centroid_x"`: Value (Double, units: micrometer) is
          the x-coordinate of the centroid of the best-fit
          ellipse of the Trace. Required.

        - `"centroid_y"`: Value (Double, units: micrometer) is
          the y-coordinate of the centroid of the best-fit
          ellipse of the Trace. Required.

        - `"a"`: Value is the ellipse axis ‘a’ which is the full width major axis (Double, units:
          micrometer). Required.

        - `"b"`: Value is the ellipse axis ‘b’ which is the full width minor axis (Double, units:
          micrometer). Required.

        - `"rot"`: Value is the ellipse axis rotation (Double,
          units: degrees). Positive angles are
          counter-clockwise and negative are clockwise,
          relative to orientation with a-axis aligned with
          +x-direction. Required.

    - `"TRUNCNORM"`: Places fascicles in the nerve with size and
      eccentricity randomly based on a truncated normal
      distribution. Rotation of fascicles is randomly drawn from
      uniform distribution from 0 to 360 degrees.

      - `"mu_fasc_diam"`: The value (Double, units: micrometer)
        is the mean fascicle diameter in the distribution.
        Required.

      - `"std_fasc_diam"`: The value (Double, units: micrometer)
        is the standard deviation of fascicle diameter in the
        distribution. Required.

      - `"n_std_diam_limit"`: The value (Double) is the limited
        number of standard deviations for the truncated normal
        fascicle diameter distribution. The value does not need
        to be an integer. Required.

      - `"num_fascicle_attempt"`: The value (Integer) is the
        number of different fascicles from the distribution that
        the program will attempt to place. Required.

        - If `"num_fascicle_attempt"` does not equal
          `"num_fascicle_placed"`, a warning is printed to the
          console instructing user to reduce the number, size,
          and/or separation of the fascicles.

      - `"num_fascicle_placed"`: The value (Integer) is the
        number of successfully placed fascicles in the nerve
        cross-section. Automatically populated.

        - If `"num_fascicle_attempt"` does not equal
          `"num_fascicle_placed"`, a warning is printed to the
          console instructing user to reduce the number, size,
          and/or separation of the fascicles.

      - `"mu_fasc_ecc"`: The value (Double) is the mean fascicle
        eccentricity in the distribution. Must be \<= 1 and \> 0. Set to 1 for circles. Required.

      - `"std_fasc_ecc"`: The value (Double, units: micrometer)
        is the standard deviation of fascicle eccentricity in
        the distribution. Required.

      - `"n_std_ecc_limit"`: The value (Double) is the limited
        number of standard deviations for the truncated normal
        fascicle eccentricity distribution. Required.

      - `"max_attempt_iter"`: The value (Integer) is the number
        of different random locations within the nerve that the
        program will attempt to place a fascicle before skipping
        it (presumably because it cannot possibly fit in the
        nerve). We recommend using 100+. Required.

      - `"min_fascicle_separation"`: The value (Double, units:
        micrometer) determines the minimum distance between
        fascicle boundaries in the binary mask image that the
        pipeline will allow without throwing an error. This
        value controls the separation required between fascicles
        in the binary mask only. There is a separate parameter
        for forcing a distance (post-deformation) of the nerve
        between fascicles and between fascicles and the nerve
        boundary in `sample.json`. Required.

      - `"seed"`: The value (Integer) initiates the random number
        generator. Required.

    - `"UNIFORM"`: Places fascicles in the nerve with size and
      eccentricity randomly based on a uniform distribution.
      Rotation of fascicles is randomly drawn from uniform
      distribution from 0 to 360 degrees.

      - `"lower_fasc_diam"`: The value (Double, units:
        micrometer) is the lower limit of the uniform
        distribution for fascicle diameter. Required.

      - `"upper_fasc_diam"`: The value (Double, units:
        micrometer) is the upper limit of the uniform
        distribution for fascicle diameter. Required.

      - `"num_fascicle_attempt"`: The value (Integer) is the
        number of different fascicles from the distribution that
        the program will attempt to place. Required.

        - If `"num_fascicle_attempt"` does not equal
          `"num_fascicle_placed"`, a warning is printed to the
          console instructing user to reduce the number, size,
          and/or separation of the fascicles.

      - `"num_fascicle_placed"`: The value (Integer) is the
        number of successfully placed fascicles in the nerve
        cross-section. Automatically populated.

        - If `"num_fascicle_attempt"` does not equal
          `"num_fascicle_placed"`, a warning is printed to the
          console instructing user to reduce the number, size,
          and/or separation of the fascicles.

      - `"lower_fasc_ecc"`: The value (Double) is the lower
        limit of the uniform distribution for fascicle
        eccentricity. Must be <= 1 and > 0. Set to 1 for circles. Required.

      - `"upper_fasc_ecc"`: The value (Double) is the upper
        limit of the uniform distribution for fascicle
        eccentricity. Must be <= 1 and > 0. Set to 1 for circles. Required.

      - `"max_attempt_iter"`: The value (Integer) is the number
        of different random locations within the nerve that the
        program will attempt to place a fascicle before skipping
        it (presumably because it cannot possibly fit in the
        nerve). We recommend using 100+. Required.

      - `"min_fascicle_separation"`: The value (Double, units:
        micrometer) determines the minimum distance between
        fascicle boundaries in the binary mask image that the
        pipeline will allow without throwing an error. This
        value controls the separation required between fascicles
        in the binary mask only. There is a separate parameter
        for forcing a distance (post-deformation) of the nerve
        between fascicles and between fascicles and the nerve
        boundary in `sample.json`. Required.

      - `"seed"`: The value (Integer) initiates the random number
        generator. Required.

## Example

```{eval-rst}
.. include:: ../../../../config/templates/mock_sample.json
   :code: javascript
```
