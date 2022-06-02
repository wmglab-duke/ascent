# Java Classes
## ModelWrapper Class
### ModelWrapper
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
contact to define the “bases” of the solution space \[1\]. For each
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

### References
1. Pelot NA, Thio BJ, Grill WM. Modeling Current Sources for Neural Stimulation in COMSOL. Front Comput Neurosci [Internet]. 2018;12:40. Available from: [https://www.frontiersin.org/article/10.3389/fncom.2018.00040](https://www.frontiersin.org/article/10.3389/fncom.2018.00040)

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
