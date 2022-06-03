Creating sample specific nerve morphologies in COMSOL
=====================================================

.. _modelwrapperaddnerve:

ModelWrapper.addNerve()
-----------------------

The ``addNerve()`` method adds the nerve components to the COMSOL
“model” object using Java. If the ``“NerveMode”`` in **Sample**
(“nerve”) is “PRESENT” (`S8 Text <S8-JSON-file-parameter-guide>`__) the
program creates a part instance of epineurium using the
``createNervePartInstance()`` method in Part (``src/model/Part.java``).
The ``addNerve()`` method then searches through all directories in
``fascicles/`` for the sample being modeled, and, for each fascicle,
assigns a path for the inner(s) and outer in a ``HashMap``. The
``HashMap`` of fascicle directories is then passed to the
``createNervePartInstance()`` method in Part which adds fascicles to the
COMSOL “model” object.

.. _partcreatenervepartinstance:

Part.createNervePartInstance()
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``createNervePartInstance()`` method in Part
(``src/model/Part.java``) creates three-dimensional representations of
the nerve sample including its endoneurium, perineurium, and epineurium.
The ``createNervePartInstance()`` method defines domain and surface
geometries and contributes them to COMSOL selections (lists of indices
for domains, surfaces, boundaries, or points), which are necessary to
later assign physics properties.

Fascicles
^^^^^^^^^

ASCENT uses CAD `sectionwise <https://www.comsol.com/fileformats>`__
files (i.e., ASCII with ``.txt`` extension containing column vectors for
x- and y-coordinates) created by the Python Sample class to define
fascicle tissue boundaries in COMSOL.

We provide the ``“use_ci”`` mode in **Model** (`S8
Text <S8-JSON-file-parameter-guide>`__) to model the perineurium using
COMSOL’s contact impedance boundary condition for fascicles with only
one inner (i.e., endoneurium) domain for each outer (i.e., perineurium)
domain (`S28 Text <S28-Definition-of-perineurium>`__). If ``“use_ci”``
mode is true, the perineurium for all fascicles with exactly one inner
and one outer is represented with a contact impedance. The pipeline does
not support control of using the contact impedance boundary condition on
a fascicle-by-fascicle basis.

The ``createNervePartInstance()`` method in Part
(``src/model/Part.java``) performs a directory dive on the output CAD
files
``samples/<sample_index>/slides/<#>/<#>/sectionwise2d/fascicles/<outer,inners>/``
from the Sample class in Python to create a fascicle for each outer.
Depending on the number of corresponding inners for each outer saved in
the file structure and the ``“use_ci”`` mode in **Model**, the program
either represents the perineurium in COMSOL as a surface with contact
impedance (FascicleCI: Fascicles with one inner per outer and if
``“use_ci”`` mode is true) or with a three-dimensional meshed domain
(FascicleMesh: Fascicles with multiple inners per outer or if
``“use_ci”`` parameter is false).

Epineurium
^^^^^^^^^^

The ``createNervePartInstance()`` method in Part
(``src/model/Part.java``) contains the operations required to represent
epineurium in COMSOL. The epineurium cross section is represented one of
two ways:

-  If ``deform_ratio`` in **Sample** is set to 1 and
   ``"DeformationMode"`` is not ``"NONE"``, the nerve shape matches the
   ``"ReshapeNerveMode"`` from **Sample** (e.g., ``"CIRCLE"``). (`S8
   Text <S8-JSON-file-parameter-guide>`__). An epineurium boundary is
   then created from this shape.

-  Otherwise, the coordinate data contained in
   ``samples/<sample_index>/slides/<#>/<#>/sectionwise2d/nerve/0/0.txt``
   is used to create a epineurium boundary.

The epineurium boundary is then extruded into the third dimension. This
is only performed if the ``“NerveMode”`` (i.e., “nerve”) in **Sample**
is ``“PRESENT”`` and ``n.tif`` is provided (`S8
Text <S8-JSON-file-parameter-guide>`__).
