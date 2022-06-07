# Java Classes
## ModelWrapper Class
The `ModelWrapper` class in Java takes inputs of the ASCENT_PROJECT_PATH
(`env.json`, [S7](S7-JSON-configuration-files) and [S8](S8-JSON-file-parameter-guide) Text) and a list of ***Run*** paths. `ModelWrapper` contains a COMSOL
“model” object, model source directory (String), model destination
directory (String), an `“IdentifierManager”` ([S26 Text](S26-Java-utility-classes)), and `HashMaps` with key-value
pairs linking COMSOL domains to unions of domains. `ModelWrapper` has
accessor methods `getModel()` for retrieving the model object, `getRoot()`
for retrieving the project path’s root String, and `getDest()` for
retrieving the default saving destination String. `ModelWrapper` also has
mutator methods for changing an instance’s root String (`setRoot()`) and
default saving destination String (`setDest()`).

`ModelWrapper’s` `main()` method starts an instance of COMSOL and loads
***Run***, ***Sample***, ***Model***, and ***Sim*** configurations as
JSON Objects into memory. We developed Java class `JSONio` ([S26 Text](S26-Java-utility-classes)) for reading and
writing JSON Objects to file.

Since each ***Run*** contains a list of ***Model*** and ***Sim***
configurations for a single ***Sample*** (note: `n_sims/` are created for
all combinations of ***Model*** and ***Sim*** for the ***Sample*** in a
***Run***), `ModelWrapper` iterates over ***Model*** configurations (e.g.,
different cuff electrodes or material assignments) to define the FEM
geometry, mesh, assign boundary conditions and physics, and solve. The
resulting FEM potentials are obtained for 1 mA applied to one of the
electrode contacts while the electric potential on the other contacts is
floating (i.e., condition of continuity); this is repeated for each
contact to define the “bases” of the solution space {cite}`Pelot2018current`. For each
***Sim***, the program then creates a superposition of the “bases” for
extracellular potentials at the coordinates defined in `fibersets/` and
`ss_coords/` (i.e., the coordinates along the length of the nerve used to
“super-sample” potentials for later creating potentials/ without the
need for COMSOL). We wrote the code such that the program will
continue with creating potentials/, `ss_bases/` (i.e., the potentials
along the length of the nerve corresponding 1:1 to the coordinates saved
in `ss_coords/`, which are added together according to the contact
weighting defined by `“active_srcs”` in *Sim* to create potentials/ for
specific fiber models), and NEURON simulations for any remaining
***Model*** indices even if the processes for a single ***Model***
fails. For each ***Model***, the program appends a Boolean to
`“models_exit_status”` in ***Run*** (true if successful, false if not
successful).

###  ModelWrapper.addNerve()

The `addNerve()` method adds the nerve components to the COMSOL “model”
object using Java. If the `“NerveMode”` in ***Sample*** (“nerve”) is
“PRESENT” ([S8 Text](S8-JSON-file-parameter-guide)) the program creates a part instance of epineurium using the
`createNervePartInstance()` method in Part (`src/model/Part.java`). The
`addNerve()` method then searches through all directories
in `fascicles/` for the sample being modeled, and, for each fascicle,
assigns a path for the inner(s) and outer in a `HashMap`. The `HashMap` of
fascicle directories is then passed to the `createNervePartInstance()`
method in Part which adds fascicles to the COMSOL “model” object.

### ModelWrapper.extractAllPotentials()
The user is unlikely to interface directly with ModelWrapper’s
`extractAllPotentials()` method in Java as it operates behind the scenes.
The method takes input arguments for the project path and a run path.
Using the run path, the method loads ***Run***, and constructs lists of
***Model*** and ***Sim*** for which it will call `extractPotentials()` for
each fiberset. COMSOL is expecting a (3 ⨉ *n*)
matrix of coordinates (Double[3][n]), defining the
(x,y,z)-coordinates for each of *n* points.

The Java COMSOL API methods `setInterpolationCoordinates()` and `getData()`
for a model object are fast compared to the time for a machine to load a
COMSOL “model” object to memory from file. Therefore, the
`extractAllPotentials()` method is intentionally configured to minimize
the number of times a “basis” COMSOL “model” object is loaded into
memory. We accomplish this by looping in the following order:
***Model***, bases, ***Sims***, fibersets (i.e., groups of fibers with
identical geometry/channels, but different (x,y)-locations and/or
longitudinal offsets), then fibers. With this approach, we load each
COMSOL “model” object only once (i.e., \*.mph members of bases/). Within
the loop, the `extractPotentials()` method constructs the bases
(double\[basis index\]\[sim index\]\[fiberset index\]\[fiber index\])
for each model (units: Volts). With the bases in memory, the program
constructs the potentials for inputs to NEURON by combining bases by
their contact weights and writes them to file within potentials/ (or
ss_bases/), which mirrors fibersets/ (or ss_coords/) in
contents.


### ModelWrapper.addMaterialDefinitions()

The user is unlikely to interface directly with the
`addMaterialDefinitions()` method in Java as it operates behind the
scenes. The method takes an input of a list of strings containing the
material functions (i.e., endoneurium, perineurium, epineurium, cuff
“fill”, cuff “insulator”, contact “conductor”, and contact “recess”),
***Model***, and a COMSOL `ModelParamGroup` for containing the material
properties as a COMSOL “Parameters Group” under COMSOL’s “Global
Definitions”. The method then loops over all material functions, creates
a new material if it does not yet exist as `“mat<#>”` using Part’s
`defineMaterial()` method, and adds the identifier (e.g., “mat1”) to the
`IdentifierManager`.

### ModelWrapper.addCuffPartMaterialAssignment()

The user is unlikely to interface directly with the
`addCuffPartMaterialAssignment()` method in Java as it operates behind the
scenes. The method loads in a cuff part primitive’s labels from its
IdentifierManager. The method loops over the list of material JSON
Objects in the “preset” cuff configuration file. For each material
function in the “preset” cuff configuration file, the method creates a
COMSOL Material Link to assign a previously defined selection in a cuff
part instance to a defined material.

### ModelWrapper.addCuffPartMaterialAssignments()

The user is unlikely to interface directly with the
`addCuffMaterialAssignments()` method in Java as it operates behind the
scenes. The method loops through all part instances in the cuff
configuration file, which is linked to ***Model*** by a string of its
file name under the “preset” key, and calls the
`addCuffMaterialAssignment()` method for each part instance. As described
in `addCuffPartMaterialAssignment()` above, a material is connected to the
selection within the part primitive by its label. In COMSOL, material
links appear in the “Materials” node. COMSOL assigns the material links
in the order of the part instances defined in the “preset” cuff
configuration file, which is important since material links overwrite
previous domain assignments. For this reason, it is important to list
part instances in “preset” cuff files in a nested order (i.e., the
outermost domains first, knowing that domains nested in space within
them will overwrite earlier domain assignments).

## Making geometries in COMSOL (Part class)
###  Part.createEnvironmentPartPrimitive()

The `createEnvironmentPartPrimitive()` method in Java
(`src/model/Part.java`) creates a “part” within the “Geometry Parts” node
of the COMSOL “model” object to generalize the cylindrical medium
surrounding the nerve and electrode. Programmatically selecting domains
and surfaces in COMSOL requires that geometry operations be contributed
to “selections” (`csel<#>`). In this simple example of a part
primitive, the `im.labels String[]` contains the string “MEDIUM” which
is used to label the COMSOL selection (`csel<#>`) for the medium domain
by association with an `IdentifierManager` ([S26 Text](S26-Java-utility-classes)). When the geometry of the
primitive is built, the resulting medium domain’s `csel<#>` can be
accessed instead with the key “MEDIUM” in the `IdentifierManager`, thereby
improving readability and accessibility when materials and boundary
conditions are assigned in the `createEnvironmentPartInstance()` method.
Furthermore, if the operations of a part primitive are modified, the
indexing of the `csel<#>` labels are automatically handled.

###  Part.createCuffPartPrimitive()

The `createCuffPartPrimitive()` method in Java (`src/model/Part.java`) is
analogous to `createEnvironmentPartPrimitive()`, except that it contains
the operations required to define cuff part geometries, which are
generally more complex. Examples of cuff part primitives include
standard geometries for contact conductors (e.g., Ribbon Contact
Primitive, Wire Contact Primitive, Circle Contact Primitive, and
Rectangular Contact Primitive), cuff insulation (e.g., Tube Cuff), cuff
fill (e.g., saline, mineral oil), and specific interactions of a cuff
insulator and electrode contact (e.g., LivaNova-inspired helical coil)
([S16 Text](S16-Library-of-part-primitives-for-electrode-contacts-and-cuffs)).

###  Part Instances

Part instances are a COMSOL Geometry Feature (`“pi<#>”`) in the
“Geometry” node based on user-defined input parameters stored in
***Model*** and default parameters for “preset” cuffs. A part instance
is an instantiation of a part primitive previously defined in the COMSOL
“model” object and will take specific form based on its input
parameters.

#### Part.createEnvironmentPartInstance()

The `createEnvironmentPartInstance()` method in Java creates a “part
instance” in COMSOL’s “Geometry” node based on a primitive previously
defined with `createEnvironmentPartPrimitive()`. This method just applies
to building the surrounding medium. The method takes inputs, with data
types and examples in parentheses: `instanceID` (String: `“pi<#>”`),
`instanceLabel` (String: “medium”), `mediumPrimitiveString` (String: Key for
the medium part stored in the `identifierManager`), an instance of
`ModelWrapper`, and ***Model*** as a JSON Object. Within the “medium” JSON
Object in ***Model***, the parameters required to instantiate the
environment part primitive are defined.

#### Part.createCuffPartInstance()

The `createCuffPartInstance()` method in Java is analogous to
`createEnvironmentPartInstance()`, but it is used to instantiate cuff part
geometries. We decided to separate these methods since all products of
`createCuffPartInstance()` will be displaced and rotated by the same cuff
shift (x,y,z) and rotation values.


####  Part.createNervePartInstance()

The `createNervePartInstance()` method in Part (`src/model/Part.java`)
creates three-dimensional representations of the nerve sample including
its endoneurium, perineurium, and epineurium. The
`createNervePartInstance()` method defines domain and surface geometries
and contributes them to COMSOL selections (lists of indices for domains,
surfaces, boundaries, or points), which are necessary to later assign
physics properties.



##### Fascicles

ASCENT uses CAD [sectionwise](https://www.comsol.com/fileformats)
 files (i.e., ASCII with `.txt`
extension containing column vectors for x- and y-coordinates) created by
the Python Sample class to define fascicle tissue boundaries in COMSOL.

We provide the `“use_ci”` mode in ***Model*** ([S8 Text](S8-JSON-file-parameter-guide)) to model the perineurium
using COMSOL’s contact impedance boundary condition for fascicles with
only one inner (i.e., endoneurium) domain for each outer (i.e.,
perineurium) domain ([S28 Text](S28-Definition-of-perineurium)). If `“use_ci”` mode is true, the perineurium for all
fascicles with exactly one inner and one outer is represented with a
contact impedance. The pipeline does not support control of using the
contact impedance boundary condition on a fascicle-by-fascicle basis.

The `createNervePartInstance()` method in Part (`src/model/Part.java`)
performs a directory dive on the output CAD files
`samples/<sample_index>/slides/<#>/<#>/sectionwise2d/fascicles/<outer,inners>/`
from the Sample class in Python to create a fascicle for
each outer. Depending on the number of corresponding inners for each
outer saved in the file structure and the `“use_ci”` mode in ***Model***,
the program either represents the perineurium in COMSOL as a surface
with contact impedance (FascicleCI: Fascicles with one inner per outer
and if `“use_ci”` mode is true) or with a three-dimensional meshed domain
(FascicleMesh: Fascicles with multiple inners per outer or if `“use_ci”`
parameter is false).

##### Epineurium

The `createNervePartInstance()` method in Part (`src/model/Part.java`)
contains the operations required to represent epineurium in COMSOL. The
epineurium cross section is represented one of two ways:
-  If `deform_ratio`
    in ***Sample*** is set to 1 and `"DeformationMode"` is not `"NONE"`,
    the nerve shape matches the `"ReshapeNerveMode"` from ***Sample***
    (e.g., `"CIRCLE"`). ([S8 Text](S8-JSON-file-parameter-guide)).
    An epineurium boundary is then created from this shape.

-  Otherwise, the coordinate data contained in
    `samples/<sample_index>/slides/<#>/<#>/sectionwise2d/nerve/0/0.txt`
    is used to create a epineurium boundary.

The epineurium boundary is then extruded into the third dimension. This
is only performed if the `“NerveMode”` (i.e., “nerve”) in ***Sample*** is
`“PRESENT”` and `n.tif` is provided ([S8 Text](S8-JSON-file-parameter-guide)).


###  Part.defineMaterial()

The user is unlikely to interface directly with the `defineMaterial()`
method in Java as it operates behind the scenes to add a new material to
the COMSOL “Materials” node under “Global Definitions”. The method takes
inputs of the material’s identifier in COMSOL (e.g., “mat1”), function
(e.g., cuff “fill”), ***Model***, a library of predefined materials
(e.g., `materials.json`), a ModelWrapper instance, and the COMSOL
ModelParamGroup for material conductivities. The `defineMaterial()` method
uses materials present in ***Model’s*** “conductivities” JSON Object to
assign to each material function in the COMSOL model (e.g., insulator,
conductor, fill, endoneurium, perineurium, epineurium, or medium). The
material value for a function key in ***Model*** is either a string for
a pre-defined material in `materials.json`, or a JSON Object (containing
unit, label, and value) for a custom material. Assigning material
conductivities to material functions in this manner enables control for
a user to reference a pre-defined material or explicitly link a custom
material to a COMSOL model. In either the case of a predefined material
in `materials.json` or custom material in ***Model***, if the material is
anisotropic, the material value is assigned a string “anisotropic” which
tells the program to look for independent `“sigma_x”`, `“sigma_y”`, and
`“sigma_z”` values in the material JSON Object.


## Java utility classes

###  IdentifierManager

In working with highly customized COMSOL FEMs, we found it convenient to
abstract away from the underlying COMSOL indexing to improve code
readability and enable scalability as models increase in geometric
complexity. We developed a class named `IdentifierManager` that allows the
user to assign their own String to identify a COMSOL geometry feature
tag (e.g., `wp<#>`, `cyl<#>`, `rev<#>`, `dif<#>`) or selection
(i.e., `csel<#>`).

We use `IdentifierManagers` to name and keep track of identifier labels
within a `PartPrimitive`. `IdentifierManagers` assigning tags for products
of individual operations to a unique “pseudonym” in
[HashMaps](https://docs.oracle.com/javase/8/docs/api/java/util/HashMap.html)
 as
a key-value pair. Additionally, we assign resulting selections
(`“csel<#>”`) to meaningful unique pseudonyms to later assign to
meshes, materials, or boundary conditions.

We keep a running total for tags of `IdentifierStates` (i.e., the total
number of uses of an individual COMSOL tag) and `HashMap` of
`IdentifierPseudonyms` (i.e., a `HashMap` containing key (pseudonym) and
value (COMSOL tag, e.g., “wp1”)).

`IdentifierManager` has a method `next()` which takes inputs of a COMSOL tag
(e.g., `wp`, `cyl`, `rev`, `dif`) or selection (i.e., `csel`) without its index
and a user’s unique pseudonym String. The method appends the next index
(starting at 1) to the COMSOL tag or selection and puts the COMSOL tag
or selection and associated pseudonym in the `IdentifierPseudonyms`
`HashMap`. The method also updates the `IdentifierStates` `HashMap` total for
the additional instance of a COMSOL tag or selection.

To later reference a COMSOL tag or selection, `IdentifierManager` has a
`get()` method which takes the input of the previously assigned pseudonym
key and returns the COMSOL tag or selection value from the
`IdentifierPseudonyms` `HashMap`.

To accommodate mesh recycling (see `ModelSearcher` below), we save a
COMSOL model’s `IdentifierManagers` to later access selections for
updating model materials and physics. Therefore, we developed
`IdentifierManager` methods `toJSONObject()` and `fromJSONObject()` which
saves an `IdentifierManager` to a JSON file and loads an `IdentifierManager`
into Java from a JSON Object, respectively.

###  JSONio

`JSONio` is a convenient Java class used for reading and writing JSON
Objects to file. The `read()` method takes an input String containing the
file path to read and returns a JSON Object to memory. The `write()`
method takes an input String containing the file path for the saving
destination and a JSON Object containing the data to write to file.

###  ModelSearcher

The `ModelSearcher` class in Java is used to look for previously created
FEM meshed geometries that can be repurposed. For example, if
***Model*** configurations differ only in their material properties or
boundary conditions and the previous ***Model’s*** \*.mph file with the
mesh (i.e., `mesh.mph`) was saved, then it is redundant to build and mesh
the same model geometry for a new ***Model*** configuration. The methods
of the `ModelSearcher` class can save enormous amounts of computation time
in parameter sweeps of ***Model*** if the mesh can be recycled. The user
is unlikely to interface directly with this method as it operates behind
the scenes, but if the user adds new parameter values to ***Model***,
then the user must also add those values to
`config/templates/mesh_dependent_model.json` to indicate whether the
added parameter value needs to match between FEMs to recycle the mesh
(explained further below). Generally, changes in geometry or meshing
parameters need to match, but changes in material properties or boundary
conditions do not, since they do not change the FEM geometry.

Specifically, this class compares ***Model*** configurations to
determine if their parameters are compatible to repurpose the geometry
and mesh from a previously generated COMSOL model using the `meshMatch()`
method. The `meshMatch()` method takes the inputs of a reference JSON
(i.e., `config/templates/mesh_dependent_model.json`, see [S7](S7-JSON-configuration-files) and [S8](S8-JSON-file-parameter-guide) Text) containing
conditions for compatibility and a JSON Object for each of two
***Model*** configurations to compare. The parameter keys correspond
one-to-one in ***Model*** and `mesh_dependent_model.json`. However, in
`mesh_dependent_model.json`, rather than numerical or categorical values
for each parameter key, the keys’ values are a Boolean indicating if the
values between two ***Model*** configurations must be identical to
define a “mesh match”. For two ***Model*** configurations to be a match,
all parameters assigned with the Boolean true in
`mesh_dependent_model.json` must be identical. ***Model***
configurations that differ only in values for parameters that are
assigned the Boolean false are considered a mesh match and do not
require that the geometry be re-meshed.

In the class’s `searchMeshMatch()` method, the program looks through all
***Model*** configurations under a given ***Sample*** and applies the
`meshMatch()` method. If a ***Model*** match is found, `searchMeshMatch`
returns a Match class, which is analogous to the `ModelWrapper` class,
using the path of the matching ***Model*** with the `fromMeshPath()`
method.


### Part.defineMaterial()

The user is unlikely to interface directly with the `defineMaterial()`
method in Java as it operates behind the scenes to add a new material to
the COMSOL “Materials” node under “Global Definitions”. The method takes
inputs of the material’s identifier in COMSOL (e.g., “mat1”), function
(e.g., cuff “fill”), ***Model***, a library of predefined materials
(e.g., `materials.json`), a ModelWrapper instance, and the COMSOL
ModelParamGroup for material conductivities. The `defineMaterial()` method
uses materials present in ***Model’s*** “conductivities” JSON Object to
assign to each material function in the COMSOL model (e.g., insulator,
conductor, fill, endoneurium, perineurium, epineurium, or medium). The
material value for a function key in ***Model*** is either a string for
a pre-defined material in `materials.json`, or a JSON Object (containing
unit, label, and value) for a custom material. Assigning material
conductivities to material functions in this manner enables control for
a user to reference a pre-defined material or explicitly link a custom
material to a COMSOL model. In either the case of a predefined material
in `materials.json` or custom material in ***Model***, if the material is
anisotropic, the material value is assigned a string “anisotropic” which
tells the program to look for independent `“sigma_x”`, `“sigma_y”`, and
`“sigma_z”` values in the material JSON Object.
