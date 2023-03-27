# model.json

Named file:
`samples/<sample_index>/models/<model_index>/model.json`

## Purpose

Contains user-defined modes and parameters to use in
constructing the FEM (**_Model_**). We provide parameterized control
of model geometry dimensions, cuff electrode, material assignment,
spatial discretization of the FEM (mesh), and solution.
Additionally, `model.json` stores meshing and solving statistics.

## Syntax

To declare this entity in
`samples/<sample_index>/models/<model_index>/model.json`, use
the following syntax:

```javascript
{
  "pseudonym": String,
  "modes": {
    "rho_perineurium": String,
    "cuff_shift": String,
    "fiber_z": String,
    "use_ci": Boolean
  },
  "medium": {
    "proximal": {
      "distant_ground": Boolean,
      "length": Double,
      "radius": Double
    },
    "distal": {
      "exist": Boolean,
      "distant_ground": Boolean,
      "length": Double,
      "radius": Double,
      "shift": {
        "x": Double,
        "y": Double,
        "z": Double
      }
    }
  },
  "inner_interp_tol": Double,
  "outer_interp_tol": Double,
  "nerve_interp_tol": Double,
  "cuff": {
    "preset": String,
    "rotate": {
      "pos_ang": Double,
      "add_ang": Double
    },
    "shift": {
      "x": Double,
      "y": Double,
      "z": Double
    }
  },
  "min_radius_enclosing_circle": Double,
  "mesh": {
  "quality_measure": String,
  "shape_order": String,
    "proximal": {
      "type": {
        "im": String,
        "name": String
      },
      "hmax": Double,
      "hmin": Double,
      "hgrad": Double,
      "hcurve": Double,
      "hnarrow": Double
    },
    "distal": {
      "type": {
        "im": String,
        "name": String
      },
      "hmax": Double,
      "hmin": Double,
      "hgrad": Double,
      "hcurve": Double,
      "hnarrow": Double
    },
    "stats": {
      "name": String,
      "quality_measure_used": String,
      "number_elements": Double,
      "min_quality": Double,
      "mean_quality": Double,
      "min_volume": Double,
      "volume": Double
      "mesh_times": {
        "distal": Double,
        "proximal": Double
      },

    }
  },
  "frequency": Double,
  "temperature": Double,
  "conductivities": {
    "recess": String,
    "medium": String,
    "fill": String,
    "insulator": String,
    "conductor": String,
    "endoneurium": String,
    "perineurium": {
      "label": String,
      "value": Double
    },
    "epineurium": String
  },
  "solver": {
    "sorder": int,
    "type": String
  },
  "solution": {
    "sol_time": Double,
    "name": String
  }
}
```

## Properties

`"pseudonym"`: This value (String) informs pipeline print statements, allowing
users to better keep track of the purpose of each configuration file. Optional.

`“modes”`: Each option controls different aspects of how Model functions.

- `“rho_perineurium”`: The value (String) is the
  `“PerineuriumResistivityMode”` that tells the program how to
  calculate the perineurium conductivity in a frequency and/or
  temperature dependent way. Required.

  - As listed in Enums ([Enums](../../Code_Hierarchy/Python.md#enums)), known `“PerineuriumResistivityModes”` include

    - `“RHO_WEERASURIYA”`: Program uses mean of circuits C and D
      from Weerasuriya 1984 \[1\] (frog sciatic nerve) ([Perineurium Properties](../../Running_ASCENT/Info.md#definition-of-perineurium)) to adjust
      perineurium conductivity to account for temperature and
      frequency (which are both stored in `model.json`).

    - `“MANUAL”`: Program uses the user-defined value of
      conductivity in “conductivities” (under “perineurium”) with
      no automated correction for frequency.

- `“cuff_shift”`: The value (String) is the `“CuffShiftMode”` that tells
  the program how to shift the cuff on the nerve ([Creating Custom Cuffs](../../Primitives_and_Cuffs/Custom_Cuffs) and [Cuff Placement on the Nerve](../../Running_ASCENT/Info.md#cuff-placement-on-nerve)). Required.

  - As listed in Enums ([Enums](../../Code_Hierarchy/Python.md#enums)), known modes include

    - `“NAIVE_ROTATION_MIN_CIRCLE_BOUNDARY”`: Program shifts the
      cuff to within a user-defined distance of the minimum
      bounding circle of the nerve sample. The direction of the
      shift is defined in the preset cuff JSON file ([Creating Custom Cuffs](../../Primitives_and_Cuffs/Custom_Cuffs) and [Cuff Placement on the Nerve](../../Running_ASCENT/Info.md#cuff-placement-on-nerve)). Since this mode does not align the cuff with the sample centroid, orientation masks (`a.tif`) are ignored.

    - `“NAIVE_ROTATION_TRACE_BOUNDARY”`: Program shifts the cuff
      to within a user-defined distance of the nerve trace
      boundary. The direction of the shift is defined in the
      preset cuff JSON file ([Creating Custom Cuffs](../../Primitives_and_Cuffs/Custom_Cuffs) and [Cuff Placement on the Nerve](../../Running_ASCENT/Info.md#cuff-placement-on-nerve)). Since this mode does not align the cuff with the sample centroid, orientation masks (`a.tif`) are ignored.

    - `“AUTO_ROTATION_MIN_CIRCLE_BOUNDARY”`: Program
      shifts/rotates the cuff to within a user-defined distance of
      the minimum bounding circle of the nerve sample to align
      with the Slide’s `“fascicle_centroid”`. The direction of the
      shift is defined in the preset cuff JSON file ([Creating Custom Cuffs](../../Primitives_and_Cuffs/Custom_Cuffs) and [Cuff Placement on the Nerve](../../Running_ASCENT/Info.md#cuff-placement-on-nerve)).

    - `“AUTO_ROTATION_MIN_TRACE_BOUNDARY”`: Program
      shifts/rotates the cuff to within a user-defined distance of
      the nerve trace boundary to align with the Slide’s
      `“fascicle_centroid”`. The direction of the shift is
      defined in the preset cuff JSON file ([Creating Custom Cuffs](../../Primitives_and_Cuffs/Custom_Cuffs) and [Cuff Placement on the Nerve](../../Running_ASCENT/Info.md#cuff-placement-on-nerve)).

    - `“NONE”`: Program keeps both the nerve centroid and cuff
      centered at (x,y) =(0,0) and no cuff rotation is performed ([Creating Custom Cuffs](../../Primitives_and_Cuffs/Custom_Cuffs) and [Cuff Placement on the Nerve](../../Running_ASCENT/Info.md#cuff-placement-on-nerve)). Note: This mode will ignore any supplied orientation image (`a.tif`).

- `“fiber_z”`: The value (String) is the `“FiberZMode”` that tells the
  program how to seed the NEURON fibers along the length of the FEM.
  In the current implementation of the pipeline, this value must be
  “EXTRUSION”. Required.

- `“use_ci”`: The value (Boolean), if true, tells the program whether
  to model fascicles (outer) that have a single inner as a sheet
  resistance (i.e., COMSOL “contact impedance”) to simplify the
  meshing of the model. If the value is false, the program will mesh
  the perineurium of all fascicles. Note that fascicles that have more
  than one inner per outer always have a meshed perineurium.

`“medium”`: The medium JSON Object contains information for the size,
position, and boundary conditions (i.e., grounded external surface) of
the proximal (i.e., cylinder containing the full length of nerve and the
cuff electrode) and distal (i.e., surrounding) medium domains. Required.

- `“proximal”`: The proximal JSON Object has keys `“distant_ground”`
  (Boolean) that sets the outer surface to ground if true (if false, sets the outer surface to "current conservation", i.e. perfectly insulating), “length”
  (Double, units: micrometer), and “radius” (Double, units:
  micrometer) of a cylindrical medium. The proximal cylindrical medium
  is centered at the origin (x,y,z)=(0,0,0), where the (x,y)-origin is
  the centroid of the nerve sample (i.e., best-fit ellipse of the
  Trace/Nerve), and extends into only the positive z-direction for the
  length of the nerve. A warning is printed to the console if the user
  sets `“distant_ground”` to true AND a distal domain exists (see
  “distal” below). Required.

- `“distal”`: The distal JSON Object has keys analogous to the
  “proximal” JSON Object, but contains additional keys “exist”
  (Boolean) and “shift” (JSON Object containing key-values pairs
  (Doubles)). The “exist” key allows the user to toggle the existence
  of the distal medium, which is intended to be used to apply coarser
  meshing parameters than in the proximal medium (which contains the
  nerve and cuff electrode along the full length of the nerve). The
  “shift” JSON Object provides control for the user to move the
  distal medium around the proximal medium (x,y,z) (Double, units:
  micrometer). Optional.

`“inner_interp_tol”`: The value (Double) sets the relative tolerance for
the representation of the inner trace(s) in COMSOL. When the value is
set to 0, the curve is jagged, and increasing the value of this
parameter increases the smoothness of the curve. COMSOL’s “closed curve”
setting interpolates the points of the curve with continuous first- and
second-order derivatives. Generally, we find an interpolation tolerance
in the range of 0.01-0.02 to be appropriate, but the user should check that the
interpolation tolerance is set correctly for their input nerve sample
morphology. See the [COMSOL Documentation](https://doc.comsol.com/5.5/doc/com.comsol.help.comsol/comsol_ref_geometry.14.038.html) for more info. Required.

`“outer_interp_tol”`: The value (Double) sets the relative tolerance for
the representation of the outer trace(s) in COMSOL. When the value is
set to 0, the curve is jagged, and increasing the value of this
parameter increases the smoothness of the curve. COMSOL’s “closed curve”
setting interpolates the points of the curve with continuous first- and
second-order derivatives. Generally, we find an interpolation tolerance
in the range of 0.01-0.02 to be appropriate, but the user should check that the
interpolation tolerance is set correctly for their input nerve sample
morphology. See the [COMSOL Documentation](https://doc.comsol.com/5.5/doc/com.comsol.help.comsol/comsol_ref_geometry.14.038.html) for more info. Required.

`“nerve_interp_tol”`: The value (Double) sets the relative tolerance for
the representation of the nerve (i.e. epineurium) trace in COMSOL. When the value is
set to 0, the curve is jagged, and increasing the value of this
parameter increases the smoothness of the curve. COMSOL’s “closed curve”
setting interpolates the points of the curve with continuous first- and
second-order derivatives. Generally, we find an interpolation tolerance
in the range of 0.001-0.005 to be appropriate, but the user should check that the
interpolation tolerance is set correctly for their input nerve sample
morphology. See the [COMSOL Documentation](https://doc.comsol.com/5.5/doc/com.comsol.help.comsol/comsol_ref_geometry.14.038.html) for more info. Required.

`“cuff”`: The cuff JSON Object contains key-value pairs that define which
cuff to model on the nerve in addition to how it is placed on the nerve
(i.e., rotation and translation). If the user would like to loop over
preset cuff designs, then they must create a **_Model_** (model index)
for each cuff preset. Required.

- `“preset”`: The value (String) indicates which cuff to model, selected
  from the list of filenames of the “preset” cuffs in
  `config/system/cuffs/<filename>.json` ([Fig 3A](https://doi.org/10.1371/journal.pcbi.1009285.g003) and [Creating Custom Cuffs](../../Primitives_and_Cuffs/Custom_Cuffs)). Required.

- `“rotate”`: Contains two keys: `“pos_ang”` (automatically populated
  based on “CuffShiftMode”, i.e., `“cuff_shift”` parameter in
  **_Model_**) and `“add_ang”` (optionally set by user to rotate cuff
  by an additional angle) ([Cuff Placement on the Nerve](../../Running_ASCENT/Info.md#cuff-placement-on-nerve)).

  - `“pos_ang”` (Double, units: degrees) is calculated by the
    pipeline for the “AUTO” CuffShiftModes ([Cuff Placement on the Nerve](../../Running_ASCENT/Info.md#cuff-placement-on-nerve)).

  - `“add_ang”` (Double, units: degrees) is user-defined and adds
    additional rotation in the counterclockwise direction. If the
    parameter is not specified, the default value is 0. Optional.

- `“shift”`: Contains three keys: “x”, “y”, and “z”. Automatically
  calculated based on “CuffShiftMode”.

  - Each key defines the translation of the cuff in the Cartesian
    coordinate system (Double, units: micrometer). The values are
    automatically populated by the pipeline based on the
    `“CuffShiftMode”` (i.e., `“cuff_shift”` parameter within
    “modes”). Origin (x,y) = (0,0) corresponds to the centroid
    of the nerve sample (or fascicle best-fit ellipse of the Trace
    if monofascicular), and shift in z-direction is along the
    proximal medium’s (i.e., the nerve’s) length relative to the
    cuff “Center” (defined in preset JSON file).

`“min_radius_enclosing_circle”`: The value (Double, units: micrometer)
is automatically defined in the program with the radius of the minimum
bounding circle of the sample, which is used for placing the cuff on the
nerve for certain CuffShiftModes. Automatically calculated.

`“mesh”`: The mesh JSON Object contains key-value pairs that define
COMSOL’s meshing parameters (required, user-defined) and resulting
meshing statistics (automatically calculated).

- `“quality_measure”`: (String) COMSOL measure to use in calculating mesh quality stats. Options include skewness, maxangle, volcircum, vollength, condition, growth. Default is "vollength" if not specified.

- `“shape_order”`: Order of geometric shape functions (String) (e.g.,
  quadratic). Required.

<!-- end list -->

- `“proximal”`: Meshing parameters for the proximal cylindrical domain
  (as defined in “medium”). Required ([Assigning Material Properties](../../Running_ASCENT/Info.md#control-of-medium-surrounding-nerve-and-cuff-electrode)).

  - `“type”`: JSON Object containing parameters/definitions specific
    to meshing discretization method (e.g., free tetrahedral
    “ftet”). We recommend free tetrahedral meshes. Required ([Assigning Material Properties](../../Running_ASCENT/Info.md#control-of-medium-surrounding-nerve-and-cuff-electrode)).

    - `“im”`: COMSOL indexing prefix (String) (e.g., free
      tetrahedral “ftet”). Required.

    - `“name”`: COMSOL system name (String) for the created mesh
      (e.g., “FreeTet”). Required.

  - `“hmax”`: Maximum element size (Double, units: micrometer). We
    recommend between 1000-4000. Required.

  - `“hmin”`: Minimum element size (Double, units: micrometer). We
    recommend 1. Required.

  - `“hgrad”`: Maximum element growth (Double). We recommend between
    1.8-2.5. Required.

  - `“hcurve”`: Curvature factor (Double). We recommend 0.2. Required.

  - `“hnarrow”`: Resolution of narrow regions (Double). We recommend 1. Required.

- `“distal”`: Meshing parameters for the distal cylindrical domain (as
  defined in “medium”). Required if distal domain present (see
  “medium”).

  - `“type”`: JSON Object containing parameters/definitions specific
    to meshing discretization method (e.g., free tetrahedral
    “ftet”). We recommend free tetrahedral meshes. Required ([Assigning Material Properties](../../Running_ASCENT/Info.md#control-of-medium-surrounding-nerve-and-cuff-electrode)).

    - `“im”`: COMSOL indexing prefix (String) (e.g., free
      tetrahedral “ftet”). Required.

    - `“name”`: COMSOL system name (String) for the created mesh
      (e.g., “FreeTet”). Required.

  - `“hmax”`: Maximum element size (Double, units: micrometer). We
    recommend between 1000-4000. Required.

  - `“hmin”`: Minimum element size (Double, units: micrometer). We
    recommend 1. Required.

  - `“hgrad”`: Maximum element growth (Double). We recommend between
    1.8-2.5. Required.

  - `“hcurve”`: Curvature factor (Double). We recommend 0.2. Required.

  - `“hnarrow”`: Resolution of narrow regions (Double). We recommend 1. Required.

- `“stats”`: Meshing statistics. See COMSOL documentation for more
  details. Automatically populated.

  - `“name”`: Mesher identity (String) which generated the mesh (i.e., COMSOL version)

  - `“quality_measure_used”`: `"quality measure"` which was used to calculate mesh statistics. (String)

  - `“number_elements”`: (Integer)

  - `“min_quality”`: (Double)

  - `“mean_quality”`: (Double)

  - `“min_volume”`: (Double)

  - `“volume”`: (Double)

  - `“mesh_times”`: JSON Object containing key value parirs storing the elapsed time (in milliseconds) for each mesh type (Proximal and Distal).

`“frequency”`: Defines the frequency value used for frequency-dependent
material conductivities (Double, unit Hz) ([Perineurium Properties](../../Running_ASCENT/Info.md#definition-of-perineurium)). Required only if
`“PerineuriumResistivityMode”` is `“RHO_WEERASURIYA”`.

`“temperature”`: Defines the temperature of the nerve environment, which
is used to define temperature-dependent material conductivity and ion
channel mechanisms in NEURON (Double, unit: Celsius). Required (user
must verify `*.MOD` files will adjust Q10 values for temperature,
verified temperature is 37 °C).

`“conductivities”`: The conductivities JSON Object contains key-value
pairs that assign materials (either previously defined in `materials.json`
(String), or explicitly defined in place (JSON Object)) to material
functions (i.e., cuff “insulator”, contact “conductor”, contact
“recess”, cuff “fill”, “endoneurium”, “perineurium”, “epineurium”).
All materials functions that are assigned to domains in the part
primitives are required. If a contact primitive contains a selection for
recessed domain, the recess material must be assigned even if there is
no recessed domain in the preset’s parameterized implementation.

- If the material is defined in place, the JSON Object value is of the
  following structure:

  - `“label”`: Communicates type of material assigned to domains
    (String). The label is used to assign materials to domains ([Assigning Material Properties](../../Running_ASCENT/Info.md#defining-and-assigning-materials-in-comsol)).
    Required.

  - `“value”`: Required. Material conductivity for isotropic materials
    (String, unit: S/m) OR (String, “anisotropic”) with additional
    keys:

    - `“sigma_x”`, `“sigma_y”`, `“sigma_z”` each with values (String,
      unit: S/m). Required.

`“solver”`: The solver JSON Object contains key-value pairs to control the
solver. Required.

- `“sorder”`: Order of solution shape functions (int) (e.g.,
  quadratic = 2). Required.

- `type`: (String) Solver to use. Options are "direct" or "iterative". Defaults to iterative if not provided, which uses less RAM but takes longer. Optional.

`“solution”`: The solution JSON Object contains key-value pairs to keep
record of FEM solver processes. Automatically populated.

- `“sol_time”`: (Double) Time (in milliseconds) elapsed in solving electric currents.

- `“name”`: Solver identity (String) used to solve electric currents (i.e., COMSOL version).

## Example

```{eval-rst}
.. include:: ../../../../config/templates/model.json
   :code: javascript
```
