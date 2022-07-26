# sample.json

Named file: `samples/<sample_index>/sample.json`

## Purpose

Instructs the pipeline on which sample-specific input data
and user-defined parameters to use for processing nerve sample
morphology inputs in preparation for 3D representation of the sample
in the FEM (**_Sample_**) ([Creating Nerve Morphology in COMSOL](../../Code_Hierarchy/Java.md#partcreatenervepartinstance)).

## Syntax

To declare this entity in
`samples/<sample_index>/sample.json`, use the following syntax:

```javascript
{
  "sample": String,
  "pseudonym": String,
  "sex": String,
  "level": String,
  "scale": {
    "scale_bar_length": Double,
    "scale_ratio": Double,
    "shrinkage": Double
  },
  "boundary_separation": {
    "fascicles": Double,
    "nerve": Double
  },
  "modes": {
    "mask_input": String,
    "scale_input": String,
    "nerve": String,
    "deform": String,
    "ci_perineurium_thickness": String,
    "reshape_nerve": String,
    "shrinkage_definition": String,
    "contour_approximation": String,
  },
  "smoothing": {
    "nerve_distance": Double,
    "fascicle_distance": Double
  },
  "image_preprocessing": {
    "fill_holes": Boolean,
    "object_removal_area": Integer
  },
  "morph_count": Integer,
  "deform_ratio": Double,
  "plot": Boolean,
  "plot_folder": Boolean,
  "render_deform": Boolean,
  "Morphology": {
    "Nerve": {
      "Area": Double
    },
    "Fascicles": [
      {
        "outer": {
          "area": Double,
          "x": Double,
          "y": Double,
          "a": Double,
          "b": Double,
          "angle": Double
        },
        "inners": [
          {
            "area": Double,
            "x": Double,
            "y": Double,
            "a": Double,
            "b": Double,
            "angle": Double
          },
          ...
        ]
      },
      ...
    ]
  }
}
```

## Properties

`“sample”`: The value (String) of this property sets the sample
name/identifier (e.g., “Rat1-1”) to relate to bookkeeping for input
morphology files ([Data Hierarchy Figure A](../../Data_Hierarchy)). The value must match the directory name in
`input/<NAME>/` that contains the input morphology files. Required.

`"pseudonym"`: This value (String) informs pipeline print statements, allowing
users to better keep track of the purpose of each configuration file. Optional.

`“sex”`: The value (String) of this property assigns the sex of the
sample. Optional, for user records only.

`“level”`: The value (String) of this property assigns the location of the
nerve sample (e.g., cervical, abdominal, pudendal). Optional, for user
records only.

`“scale”`

- `“scale_bar_length”`: The value (Double, units: micrometer) is the
  length of the scale bar in the binary image of the scale bar
  provided (`s.tif`, note that the scale bar must be oriented
  horizontally). Required if scale_input = "MASK".

- `“scale_ratio”`: The value (Double, units: micrometers/pixel) is
  the ratio of micrometers per pixel for the input mask(s).
  Required if scale_input = "RATIO".

- `“shrinkage”`: The value (Double) is the shrinkage correction for the
  nerve morphology binary images provided as a decimal (e.g., 0.20
  results in a 20% expansion of the nerve, and 0 results in no
  shrinkage correction of the nerve). Required, must be greater than 0. Note: Shrinkage correction scaling is linear (i.e. a nerve with diameter d and area a scaled by scaling factor s will have a final diameter of d_final=d\*(1+s) and a final area a_final = a\*(1+s)<sup>2</sup>)

  <!-- end list -->

`“boundary_separation”`

- `“fascicles”`: The value (Double, units: micrometer) is the minimum
  distance required between boundaries of adjacent fascicles
  (post-deformation, see Deformable in [Python Morphology Classes](../../Code_Hierarchy/Python.md#python-classes-for-representing-nerve-morphology-sample))). Required for samples with
  multiple fascicles.

  - Note that this is a distinct parameter from
    `“min_fascicle_separation”` in `mock_sample.json`, which
    controls the minimum distance between fascicles in the binary
    image mask inputs to the pipeline, which is later deformed to
    fit in the cuff electrode using Deformable ([Python Morphology Classes](../../Code_Hierarchy/Python.md#python-classes-for-representing-nerve-morphology-sample))).

- `“nerve”`: The value (Double, units: micrometer) is the minimum
  distance required between the boundaries of a fascicle and the nerve
  (post-deformation, see Deformable in [Python Morphology Classes](../../Code_Hierarchy/Python.md#python-classes-for-representing-nerve-morphology-sample))). Required if “nerve” in
  **_Sample_** is “PRESENT”.

`“modes”`:

- `“mask_input”`: The value (String) is the `“MaskInputMode”` that tells
  the program which segmented histology images to expect as inputs for
  fascicles. Required.

  - As listed in Enums ([Enums](../../Code_Hierarchy/Python.md#enums)), modes include

    1. `“INNERS”`: Program expects segmented images of only inner
       fascicle boundaries.

    2. `“INNER_AND_OUTER_SEPARATE”`: Program expects segmented
       image of inners in one file and segmented image of outers in
       another file.

    3. `“INNER_AND_OUTER_COMPILED”`: Program expects a single
       segmented image containing boundaries of both inners and
       outers.

- `“scale_input”`: The value (String) is the `“ScaleInputMode”`
  that tells the program which type of scale input to look for.

  - As listed in Enums ([Enums](../../Code_Hierarchy/Python.md#enums)), known `“ScaleInputModes”` include

    1. `“MASK”`: The program will determine image scale from the user's scale bar mask image and the `scale_bar_length` parameter.
    2. `“RATIO”`: The program will use the scale directly specified in `scale_ratio`. If using this option, a scale bar image need not be
       provided.

- `“nerve”`: The value (String) is the `“NerveMode”` that tells the
  program if there is an outer nerve boundary (epineurium) segmented
  image to incorporate into the model. Required.

  - As listed in Enums ([Enums](../../Code_Hierarchy/Python.md#enums)), known modes include

    1. `“PRESENT”`: Program expects a segmented image for a nerve
       (`n.tif`) to incorporate into the model. The value must be
       PRESENT if multifascicular nerve, but can also be PRESENT
       if monofascicular.

    2. `“NOT_PRESENT”`: Program does not try to incorporate a
       nerve boundary into the model. The value cannot be
       `NOT_PRESENT` if multifascicular nerve, but can be
       `NOT_PRESENT` if monofascicular.

- `“deform”`: The value (String) is the `“DeformationMode”` that tells the
  program which method to use to deform the nerve within the cuff. If
  the `“NerveMode”` (i.e., “nerve” parameter) is defined as
  `“NOT_PRESENT”` then the `“DeformationMode”` (i.e., “deform”
  parameter) must be `“NONE”`. Required.

  - As listed in Enums ([Enums](../../Code_Hierarchy/Python.md#enums)), known modes include

    1. `“NONE”`: The program does not deform the nerve when it is
       placed in the cuff electrode. In the pipeline’s current
       implementation, this should be the value for all nerve
       samples without epineurium (i.e., `“NOT_PRESENT”` for
       “nerve”).

    2. `“PHYSICS”`: The program uses a physics-based deformation of
       the nerve to the final inner profile of the nerve cuff,
       morphing from the original trace towards a circular trace.
       In the pipeline’s current implementation, this is the
       only `“DeformationMode”` for deforming compound nerve
       samples. See `“deform_ratio”` below; if `deform_ratio = 0`,
       then the original nerve trace is used and if `deform_ratio = 1`, then the nerve trace will be made circular.

- `“ci_perineurium_thickness”`: The value (String) is the
  `“PerineuriumThicknessMode”` that tells the program which method to
  use to define perineurium thickness. Required.

  - As listed in Enums ([Enums](../../Code_Hierarchy/Python.md#enums)), known `“PerineuriumThicknessModes”` include

    1. `“MEASURED”`: The program determines the average thickness of the
       perineurium using the provided inner and outer boundaries (i.e.,
       `“MaskInputMode”`: `INNER_AND_OUTER_SEPARATE` or
       `INNER_AND_OUTER_COMPILED`). The thickness is determined by
       finding the half the difference in diameters of the circles with
       the same areas as the inner and outer traces of the fascicle.

    2. Linear relationships between fascicle diameter and perineurium
       thickness as stored in `config/system/ci_peri_thickness.json`:

    - `“GRINBERG_2008”`
    - `“PIG_VN_INHOUSE_200523”`
    - `“RAT_VN_INHOUSE_200601”`
    - `“HUMAN_VN_INHOUSE_200601”`

- `“reshape_nerve”`: The value (String) is the `“ReshapeNerveMode”`
  that tells the program which final nerve profile
  (post-deformation) to use when “deform” is set to `“PHYSICS”`.
  Required.

  - As listed in Enums ([Enums](../../Code_Hierarchy/Python.md#enums)), known `“ReshapeNerveModes”` include

    1. `“CIRCLE”`: The program creates a circular nerve boundary
       with a preserved cross-sectional area (i.e., for multifascicular nerves/nerves that have epineurium).
    2. `“NONE”`: The program does not deform the nerve boundary (i.e., for monofascicular nerves/nerves that do not have epineurium).

- `“shrinkage_definition”`: The value (String) is the `“ShrinkageMode”`
  that tells the program how to interpret the "scale"->"shrinkage" parameter, which is provided as a decimal (i.e., 0.2 = 20%).
  Optional, but assumes the mode "LENGTH_FORWARDS if omitted, since this was the original behavior before this mode was added.

  - As listed in Enums ([Enums](../../Code_Hierarchy/Python.md#enums)), known `“ShrinkageModes”` include

    1. `“LENGTH_BACKWARDS”`: The value for "scale"->"shrinkage" refers to how much the length (e.g., radius, diameter, or perimeter)
       of the nerve cross section was reduced from the fresh tissue to the imaged tissue.
       - Formula: r_post = r_original \* (1-shrinkage)
    2. `“LENGTH_FORWARDS”`: The value for "scale"->"shrinkage" refers to how much the length (e.g., radius, diameter, or perimeter)
       of the nerve cross section increases from the imaged tissue to the fresh tissue.
       - Formula: r_post = r_original / (1+shrinkage)
    3. `“AREA_BACKWARDS”`: The value for "scale"->"shrinkage" refers to how much the area
       of the nerve cross section was reduced from the fresh tissue to the imaged tissue.
       - Formula: A_post = A_original \* (1-shrinkage)
    4. `“AREA_FORWARDS”`: The value for "scale"->"shrinkage" refers to how much the area
       of the nerve cross section increases from the imaged tissue to the fresh tissue.
       - Formula: A_post = A_original / (1+shrinkage)

- `“contour_approximation”`: The value (String) is the `“ContourMode”`
  that tells the program which method to use for approximating contours derived from
  input morphology masks. See the [OpenCV Contour Documentation](https://docs.opencv.org/4.x/d4/d73/tutorial_py_contours_begin.html) for more information on how these modes function.

  - As listed in Enums ([Enums](../../Code_Hierarchy/Python.md#enums)), known `“ContourModes”` include:

    1. `“SIMPLE”`: Contours are generated using cv2.CHAIN_APPROX_SIMPLE.
    2. `“NONE”`: Contours are generated using cv2.CHAIN_APPROX_NONE.

`“smoothing”`: Smoothing is applied via a dilating the nerve/fascicle boundary by a specified distance value and then shrinking it by that same value.

- `“nerve_distance”`: Amount (Double) to smooth nerve boundary. Units of micrometers.

- `“fascicle_distance”`: Amount (Double) to smooth fascicle boundaries (inners and outers). Units of micrometers.

<!-- end list -->

`“image_preprocessing”`: Operations applied to the input masks before analysis.

- `“fill_holes”`: The value (Boolean) indicates whether to fill gaps in the binary masks. If true, any areas of black pixels completely enclosed by white pixels will be turned white.

- `“object_removal_area”`: The value (Integer) indicates the maximum size of islands to remove from the binary masks. Any isolated islands of white pixels with area less than or equal to object_removal_area will be turned black. Units of pixels.

<!-- end list -->

`“morph_count”`: The value (Integer) can be used to set the number of
intermediately deformed nerve traces between the `boundary_start` and
`boundary_end` in Deformable ([Python Morphology Classes](../../Code_Hierarchy/Python.md#python-classes-for-representing-nerve-morphology-sample))) if the `“DeformationMode”` is “PHYSCIS”. An
excessively large number for `morph_count` will slow down the deformation
process, though a number that is too small could result in fascicles
“escaping” from the nerve. Optional; if not specified default value is 36.

`“deform_ratio”`: The value (Double, range: 0 to 1) can be used to deform
a nerve if `“DeformationMode”` is `“PHYSICS”` to an intermediately deformed
`boundary_end`. For example, if the `“ReshapeNerveMode”` is `“CIRCLE”` and
`deform_ratio = 1`, then the `boundary_end` will be a circle. However, if
the `“ReshapeNerveMode”` is `“CIRCLE”` and `deform_ratio = 0`, the
`boundary_end` will be the original nerve trace. A value between 0 and 1
will result in a partially deformed nerve “on the way” to the final
circle nerve boundary. Optional, but default value is 1 if not defined
explicitly. Note: if `deform_ratio` = 0, no changes to the nerve boundary will
occur, but the physics system will ensure the requirements in `"boundary_separation"` are met.

`“plot”`: The value (Boolean) determines whether the program
will generate output plots of sample morphology. If true, plots are generated,
if false, no plots are generated

`“plot_folder”`: The value (Boolean) describes plotting behavior (if enabled).
If true, plots are generated in the folder samples/<sample_index>/plots, if
false, plots will pop up in a window.

`"render_deform"`: The value (Boolean) if true, causes the pipeline to generated
a popup window and display a video of sample deformation as it occurs.

`“Morphology”`: This JSON Object is used to store information about the
area and best-fit ellipse information of the nerve and fascicles (outer
and inners). The user does not set values to these JSON structures, but
they are a convenient record of the nerve morphometry for assigning
model attributes based on the anatomy and data analysis. Units:
micrometer<sup>2</sup> (area); micrometer (length). User does NOT
manually set these values. Automatically populated. The values `a` and `b` are
the full width and height of the ellipse major and minor axes, respectively
(i.e., analogous to diameter rather than radius of a circle).

`"rotation"`: The value (Double) instructs the pipeline to rotate the nerve about its centroid by the specified amount (units = Degrees).
This parameter may NOT be used if providing an orientation tif image (See [Morphology Input Files](../../Running_ASCENT/Info.md#morphology-input-files)).

## Example

```{eval-rst}
.. include:: ../../../../config/templates/sample.json
   :code: javascript
```
