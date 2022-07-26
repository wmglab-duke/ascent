JSON Configuration Parameter Guide
==================================

Notes:

See  :doc:`JSON Overview <../JSON_overview>`  for a summary of
the contents and usage of each of the following JSON files used in
ASCENT.

``"//"`` is not valid JSON syntax; comments are not possible in JSON.
However, we sparingly used this notation in the JSON examples below to
provide context or more information about the associated line. Each
value following a key in the syntax denotes the *type* of the value, not
its literal value: "[<Type X>, …]" syntax indicates that the type is an
array of Type X. Occasionally, a single value may be substituted for the
list if only a single value is desired, but this functionality differs
between keys, so be sure to read the documentation before attempting for
any given key-value pair. If a parameter is optional, the entire
key-value can be omitted from the JSON file and the default value will
be used.

For calculated values, the user can either keep the key with a dummy
value or remove the key entirely when setting up JSON files for a
pipeline run.

JSON Object names, keys, and values (e.g., filename strings) are
case-sensitive.

The order of key-value pairs within a JSON Object does not matter.
Saving/loading the file to/from memory is likely to reorder the contents
of the file.

.. toctree::
   :maxdepth: 1
   :caption: Standard User Configuration Files

   run
   sample
   model
   sim

Special Use Configuration Files
##################################

.. toctree::
   :maxdepth: 1

   mock_sample
   query_criteria


System Configuration Files
##################################

.. toctree::
   :maxdepth: 1

   env
   exceptions
   materials
   ci_peri_thickness
   mesh_dependent_model
