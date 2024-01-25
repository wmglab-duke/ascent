# Modeling Neural Recording

This feature is the first introduction of multiple cuffs within the ASCENT pipeline. Begin setting up a run as usual with ASCENT (refer to [Getting Started](Getting_Started.md) for guidance and a tutorial). To use our pipeline to model neural recording, two major elements need to be present within the JSON configuration files. To prompt the pipeline to model neural recording of single fiber action potentials (SFAPs), the user should first provide a list of two JSON Objects to the `cuff` property within the **_Model_** configuration file. Each JSON Object within this list should have all the original required cuff properties outlined in [Model File](JSON/JSON_parameters/model.md), and an additional "index" property indicating whether the given JSON Object will be used for the stimulation cuff (index = 0) or the recording cuff (index = 1). The second major element is defining the electrode contact weights in the **_Sim_** file. As with a original single cuff ASCENT run through, the `active_srcs` property in this file contains key-value pairs of contact weights for each preset cuff (as described in [Sim File](JSON/JSON_parameters/sim.md)). Now, for modeling recording, the user should add an additional `active_recs` property that serves the same purpose for the recording cuff. For these two properties, the user must add an additional key-value pair called `cuff_index`, which matches the weighting properties to the cuff indices we defined in the **_Model_** file. Remember to include any cuff presets for both the stimulation and recording cuffs in `config/system/cuffs`. Run the pipeline as usual from the root directory with `python run pipeline <insert run index>`.

Example input files modeling stimulation and recording from a rat vagus nerve can be found in `examples\cap_tutorial`.


## Pipeline Outputs

When running a model with a recording cuff, in addition to the standard stimulation cuff output files, the pipeline will produce an output .dat file for every n_sim generated, called `SFAP_time`, containing the recorded SFAP collected by the recording cuff. Each SFAP file has a column for the stimulation waveform's time points (ms) and a column for corresponding recorded SFAP (uV).

Optionally, the user can set the `saving > cap_recording > Imembrane_matrix` boolean variable in the **_Simulation_** file to `true` to save a transmembrane (TM) current matrix for each fiber which contains all the TM currents of every compartment across time.


## Current Limitations

- The multiple cuff configuration is currently limited to two cuffs, with one designated as the stimulation cuff and the other designated as the recording cuff. The use of multiple cuffs for other purposes has not been tested.


## Analysis Scripts

### Plotting Single Fiber Action Potentials (SFAPs)

The `examples\analysis\plot_SFAPs.py` script allows users to visualize the recorded single fiber action potentials (SFAPs) that resulted from modeling the neural recordings. The user should open the script and update the `sample`, `model`, and `sim` number accordingly in the call to query, as in the other analysis scripts. The user may plot the SFAPs from all the fibers simulated (default behavior), controlled by the `all_fibers` input boolean argument to the call to the query class' `sfap_data` function. Alternatively, the user may choose to indicate a subset of fiber indices to plot using the `fiber_indices` variable at the top of the script. If both variables are provided, and `all_fibers` is True, the `fiber_indices` are ignored and all fibers will be provided. Run the script from the ascent root directory with the command `python examples\analysis\plot_SFAPs.py`.

### Plotting Compound Action Potentials (CAPs)
The `examples\analysis\plot_CNAP.py` script allows users to visualize the combined action potentials of multiple fibers. The user should open the script and update the `sample`, `model`, and `sim` number accordingly in the call to query, as in the other analysis scripts. As described above, the user may plot the combined SFAPs from all simulated fibers (default behavior), or may choose to only visualize a subset of fibers by indicating their indices in the `fiber_indices` variable. Run the script from the ascent root directory with the command `python examples\analysis\plot_CNAP.py`.

### Generating Current Templates per Fiber Diameter

In `examples\analysis`, there is a script called `generate_templates.py` which allows users to generate transmembrane current action potential _templates_ for each fiber diameter in a given simulation. These templates require the transmembrane current matrices to be saved, as described above. The templates can be used in conjunction with the following MATLAB repository (https://github.com/eurypt/CAPulator) to simulate whole-nerve fiber populations efficiently with a a speed up of 27,000 - 1,900,000x in terms of CPU hours. <reference paper DOI>. Rather than simulating every action potential of every nerve fber, the template method uses the action potential from a _single point in space_ and a few _discrete nerve fiber diameters_ to interpolate the action potential at _every point in space_ across _all fiber diameters_ present in the nerve. See the publication for more details.

To generate the templates, open the script and update the `sample`, `model`, `sim`, and `fiber` values at the top of the file accordingly. The `fiber` variable refers to the fiber number within each generated n_sim. Then, run the script from the ascent root directory with the command `python examples\analysis\generate_templates.py`. The action potential templates are expected to differ in latency depending on the stimulation model parameters, and the templates differ across fiber types. Thus, the user should run the script for each distinct set of stimulation parameters or fiber types.