# Creating Mock Morphology
MockSample is a Python class that manages the *data* and contains all
operations to create binary masks of mock nerve morphology (i.e., nerve:
`n.tif`, inners: `i.tif`, and scale bar: `s.tif`) to use as inputs to the
pipeline.

The user defines the parameter values in
`config/user/mock_samples/<mock_sample_index>.json` (with a template
provided in `config/templates/mock_sample.json`). The mock sample
morphology is then created using the JSON file by executing `"python run
mock_morphology_generator <mock_sample_index>"` at the project
root. The mock morphology generator uses the MockSample Python class to
create binary images of the nerve, inner perineurium traces (fascicles),
and the scale bar in `input/<NAME>/` (NAME is analogous to the
"sample" parameter in ***Sample***, following the standard naming
convention ([JSON Configuration Files](JSON/index))), which allow the pipeline to function as if binary
images of segmented histology were provided. The
`<mock_sample_index>.json` file and the resulting segmented nerve
morphology files are automatically saved in `input/<NAME>/`.

MockSample is Exceptionable, Configurable, and has instance attributes
of "nerve" and a list "fascicles". After the MockSample class is
initialized, a `mock_sample.json` file is added to the class instance.
The `mock_morphology_generator.py` script configures an instance of the
MockSample class using the first input argument, which references the
index of a JSON file stored in `config/user/mock_samples/`.

In `mock_morphology_generator.py`, MockSample’s methods `make_nerve()`
and `make_fascicles()` are called to create ellipses for the nerve and
fascicles in memory based on the parameters in the `mock_sample.json`
file. MockSample’s methods ensure that the fascicles have a minimum
distance between each fascicle boundary and the nerve and between
fascicle boundaries. For details on the parameters that define sample morphology using our mock nerve morphology generator, see [JSON Overview](JSON/JSON_overview) for a description of mock_sample.json and [Mock Sample Parameters](JSON/JSON_parameters/mock_sample) for details of the syntax/data type of the key-value parameter pairs required to define a mock sample. Lastly, MockSample’s `make_masks()` method is called
on the class instance to create binary masks and save them as TIFs in
the `input/<NAME>/` directory.
