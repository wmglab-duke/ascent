# Testing ASCENT

Testing in ASCENT is largely ad hoc, and sequestered in feature branches.
Starting with v1.5.0, ASCENT developers use the values in the /integration_tests
directory to test new features and public releases against the previous release.
Future releases will include more integration tests that include features not
captured by existing tests.

ASCENT users may want to use integration tests to debug their installation or
validate feature development. If your installation fails integration tests after,
debugging, please create an issue on GitHub with a detailed summary of your
environment.

## Unit Tests

Unit testing is a work in progress. Currently unit tests exist for
* Trace class
* Saveable class

## Integration Tests

The folders in `/tests/integration_tests` specify one run configuration and
its corresponding archived outputs for the latest release of ASCENT (v1.5.0). The
integration test script `/tests/integration.py` will run the configuration
in the local ASCENT installation, copy the results from the `/samples` folder
to an `/output` folder, compare the local run with the `/tests/integration_tests/`
archived outputs, and save a line-by-line file difference in `/diff` folder.

To run integration tests,
1. Go to the ASCENT root directory from the command line.
2. Run the command `python tests/integration.py <test_name>` where
`<test_name>` is the name of a folder in `/tests/integration_tests`.
3. Review test model outputs in the `/output` folder.
4. Compare test model outputs with archived outputs in the `/diff` folder.

### Integration.py Command Line Arguments
 - `<test folder>` (str, required): The test folder in /tests/integration_tests
 - `--save` (bool): Whether to overwrite the <test folder>. Used to create
new tests.
 - `--skip-setup` (bool): If true, assumes an /output folder exists
for <test folder> and skips re-running models.
 - `--skip-test` (bool): If true, only runs the test models, but does
not compare with saved values.
 - `--subtest` (str): Options are `pre_java`, `java`, `neuron`, or `full` (default).
Full tests the full ASCENT pipeline, while the other subtests compares output
from the corresponding steps.

### Available Tests

### 2147483000_tutorial-v150

**Tested features:**
* ASCENT's tutorial model configuration
* "mask_input": "INNER_AND_OUTER_COMPILED"
* "nerve": "NOT_PRESENT"
* "deform": "NONE"
* "ci_perineurium_thickness": "MEASURED"
* "use_ci": true
* "cuff_shift": "AUTO_ROTATION_MIN_CIRCLE_BOUNDARY"
* "fibers" "xy_parameters" "mode": "WHEEL"

### 2147483001_mock-v150

**Tested features:**
* Mock_morphology_generator.py
* "mask_input": "INNERS"
* "nerve": "PRESENT"
* "deform": "PHYSICS"
* "ci_perineurium_thickness": "HUMAN_VN_INHOUSE_200601"
* "use_ci": true

### 2147483002_full-v150

**Tested features:**
* Realistic human vagus nerve geometry
* Small fascicles
* Peanut fascicles
* Large and small fiber diameters (16 um, 2 um)
* "mask_input": "INNERS_AND_OUTERS_COMPILED"
* "use_ci": false
* "fibers" "xy_parameters" "mode": "CENTROID"

### 2147483003_explicit-v150

**Tested features:**
* Explicit fiber locations
* "fibers" "xy_parameters" "mode": "EXPLICIT"
* Swept mesh
* "mesh" "nerve": "Sweep"

### New Tests

New integration tests can be created as follows:
1. Create a new folder in `tests/integration_tests/` with the format
`<test_index>_<test_name>`. Please use an integer between 2147483000
and 2147483647 that has not been used by another test.
2. Place the run configuration files in the test folder, i.e.
   (`*.tiff` OR `mock.json`, `sample.json`, `sim.json`, `model.json`)
3. Run `python tests/integration.py <test_name> --save`

With the --save parameter, the `samples/test_index` folder for the local run will be copied to the
new `tests/integration_tests/<test_name>` folder. Once complete, you may
delete the `samples/<test_index>` and run the integration test normally.

### Developer Notes
Integration tests can be used at any point during development to probe
changes to the output, but must be used when merging to master. There are
currently no automated checks to ensure integration tests have been run.
Follow these steps to ensure that integration tests are completed and documented:

1. Update your local master branch with `git checkout master` and `git pull`
2. (Optional) Create `-master` integration tests to test the difference between
current master branch and feature branch. For example:
   1. `mkdir tests/integration_tests/2147483000_tutorial-master`
   2. `cp tests/integration_tests/2147483000_tutorial-v150/c.tif tests/integration_tests/2147483000_tutorial-master/c.tif`
      1. Repeat these steps for all .tif files, sample.json, model.json, and sim.json
   3. Create tests with as above, e.g. `python tests/integration.py 2147483000_tutorial --save`
3. Merge the local master branch to your feature branch.
4. If any input parameters were changed, edit the functions in `tests/convert_configs.py`
to convert the previous version configurations to new formats. See notes within conver_configs.py.
   1. Note that some subtests are expected to fail if inputs change.
5. Run available integration tests as above.
6. Review the test output in the `/diff` and `/output` folders. Debug any unacceptable
differences between the local branch and archived values (> ~1%).
7. Upload /tests/integration_tests, /output and /diff folders to Box and create a
README describing expected differences between ASCENT versions.
8. Commit changes to `tests/convert_configs.py` and new tests.
9. Create merge request and continue with merge.

Before each ASCENT release, also follow these steps:

10. Execute steps 1-7 above, including step 2. Instead of `-master` use the release version number `-vXXX`.
11. Delete tests from the previous version.
12. Delete irrelevant conversion functions from `tests/convert_configs.py`
13. Commit new version tests and convert_configs.py
