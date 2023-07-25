# ASCENT on oSPARC

The [oSPARC platform](https://osparc.io/ hosts two publicly accessible implementations of ASCENT. From the [oSPARC documentation](https://docs.osparc.io/#/): "The aim of o²S²PARC is to establish a comprehensive, freely accessible, intuitive, and interactive online platform for simulating peripheral nerve system neuromodulation/stimulation and its impact on organ physiology in a precise and predictive manner." ASCENT is available on oSPARC in two modes: guided mode, where you can choose from a limited selection of parameters to simulate activation thresholds, and the full implementation of ASCENT. The [oSPARC documentation](https://docs.osparc.io/#/) provides general instructions on using the oSPARC platform; the instructions below describe how to set up a run of ASCENT on oSPARC using either guided mode or the full implementation.

````{tab} Guided Mode
_The guided mode implementation of ASCENT on oSPARC enables simulation of activation thresholds for neural fibers using extracellular potentials from pre-solved finite element models. Users select a value for each parameter from drop-down menus._
```{tip}
Remember to reference the [oSPARC documentation](https://docs.osparc.io/#/) for more information on how to navigate the platform.
```
1. Create a new study using the "ASCENT Guided Mode" template.
2. Use the GUI in the "ascent-runner" node, located in the middle of the top task bar, to choose your desired parameters, and then click the "Run" button.
3. Once "ascent-runner" finishes, open the Jupyter ASCENT node. Open a terminal instance, and enter the commands:
  1. `cd work/workspace`
  2. `bash run_first.sh`
4. Threshold heatmaps will be created in `examples/analysis`
````
````{tab} Full Implementation

_The full ASCENT pipeline can be executed on oSPARC._

1. Create a new study, using either the "ASCENT Tutorial" template (See the [ASCENT tutorial](../Getting_Started.md#setting-up-a-run-of-ascent)) or the "ASCENT Base" template to set up your personalized simulation.
2. If using the tutorial template, the tutorial configs are already arranged under run index 0. If using the base template, create ASCENT's configuration files, per standard [ASCENT usage](Usage.md).
3. Open a terminal instance from the _Launcher_ tab.
4. Ensure you are in ASCENT's root directory. If not, change your working directory to ASCENT's root folder using `cd ~/work/workspace/ascent`.
5. Run ASCENT as normal using the [command line](command_line_args.rst)).
6. When running the analysis script, save the figures in your chosen location using plt.savefig().

```{note}
Only one COMSOL license seat is available on oSPARC. When running the pipeline, you can use the `--wait-for-license` [command line argument](command_line_args.rst) to specify an amount of time to wait for the COMSOL license to become available.
```
````
