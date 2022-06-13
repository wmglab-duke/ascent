# NEURON Files
## NEURON Wrapper.hoc

The ```Wrapper.hoc``` file coordinates all program operations to create a
biophysically realistic discrete cable fiber model, simulate the fiber’s
response to extracellular and intracellular stimulation, and record the
response of the fiber. For each fiber simulated in NEURON, outputs are
saved to ```<n_sim_index>/data/outputs/```. For simulations running an
activation or block threshold protocol, data outputs include threshold
current amplitudes. For simulation of fiber response to set amplitudes,
the user may save state variables at each compartment in NEURON to file
at discrete times and/or locations.

###  Create fiber model

Based on the flag for "fiber\_type" set in ```launch.hoc``` (associated by a
fiber type parameter in ```fiber_z.json``` and ```FiberGeometryMode``` ([S8 Text](S8-JSON-file-parameter-guide))),
```Wrapper.hoc``` loads the corresponding template for defining fiber geometry
discretization, i.e., ```"GeometryBuilder.hoc"``` for myelinated fibers and
```"cFiberBuilder.hoc"``` for unmyelinated fibers. For all fiber types, the
segments created and connected in NEURON have lengths that correspond to
the coordinates of the input potentials.

###  Intracellular stimulus

For simulations of block threshold, an intracellular test pulse is
delivered at one end of the fiber to test if the cuff electrode (i.e.,
placed between the intracellular stimulus and the site of detecting
action potentials) is blocking action potentials ([Simulation Protocols](../Running_ASCENT/Info.md#simulation-protocols)). The intracellular
stimulation parameters are defined in ***Sim*** and are defined as
parameters in NEURON within the ```launch.hoc``` file. The parameters in
***Sim*** control the pulse delay, pulse width, pulse repetition
frequency, pulse amplitude, and node/section index of the intracellular
stimulus ([Sim Parameters](../JSON/JSON_parameters/sim)). For simulating activation thresholds, the intracellular
stimulation amplitude should be set to zero.

###  Extracellular stimulus

To simulate response of individual fibers to electrical stimulation, we
use NEURON’s extracellular mechanisms to apply the electric potential
from COMSOL at each segment of the cable model as a time-varying signal.
We load in the stimulation waveform from a ```n_sim’s``` ```data/inputs/```
directory using the ```VeTime_read()``` procedure within
```ExtracellularStim_Time.hoc```. The saved stimulation waveform is unscaled,
meaning the maximum current magnitude at any timestep is +/-1.
Analogously, we read in the potentials for the fiber being simulated
from ```data/inputs/``` using the ```VeSpace_read()``` procedure within
```ExtracellularStim_Space.hoc```.

###  Recording

The NEURON simulation code contains functionality ready to record and
save to file the values of state variables at discrete spatial locations
for all times and/or at discrete times for all spatial locations (i.e.,
nodes of Ranvier for myelinated fibers or sections for unmyelinated
fibers) for applied extracellular potential, intracellular stimulation
amplitude, transmembrane potential, and gating parameters using
```Recording.hoc```. The recording tools are particularly useful for
generating data to troubleshoot and visualize simulations.

###  RunSim

Our procedure ```RunSim``` is responsible for simulating the response of the
model fiber to intracellular and extracellular stimulation. Before the
simulation starts, the procedure adds action potential counters to look
for a rise above a threshold transmembrane potential.

So that each fiber reaches a steady-state before the simulation starts,
the ```RunSim``` procedure initializes the fiber by stepping through large
time steps with no extracellular potential applied to each compartment.
```RunSim``` then loops over each time step, and, while updating the value of
extracellular potential at each fiber segment, records the values of
flagged state variables as necessary.

At the end of ```RunSim’s``` loop over all time steps, if the user is
searching for threshold current amplitudes, the method evaluates if the
extracellular stimulation amplitude was above or below threshold, as
indicated by the presence or absence of an action potential for
activation and block thresholds, respectively.

###  FindThresh

The procedure ```FindThresh``` performs a binary search for activation and
block thresholds ([Simulation Protocols](../Running_ASCENT/Info.md#simulation-protocols)).

###  Save outputs to file

At the end of the NEURON simulation, the program saves state variables
as indicated with saveflags, CPU time, and threshold values. Output
files are saved to the ```data/outputs/``` directory within its ```n_sim``` folder.

## NEURON launch.hoc
The ```launch.hoc``` file defines the parameters and simulation protocol for
modeling fiber response to electrical stimulation in NEURON and is
automatically populated based on parameters in ***Model*** and
***Sim***. The ```launch.hoc``` file is created by the ```HocWriter``` class.
Parameters defined in ```launch.hoc``` span the categories of: environment
(i.e., temperature from ***Model***), simulation time (i.e., time step,
duration of simulation from ***Sim***), fiber parameters (i.e., flags
for fiber geometry and channels, number of fiber nodes from ***Model***,
***Sim***, and ```config/system/fiber_z.json```), intracellular stimulation
(i.e., delay from start of simulation, amplitude, pulse duration, pulse
repetition frequency from ***Sim***), extracellular stimulation (i.e.,
path to waveform file in ```n_sim/``` folder which is always
```data/inputs/waveform.dat```), flags to define the model parameters that
should be recorded (i.e., Vm(t), Gating(t), Vm(x), Gating(x) from
***Sim***), the locations at which to record the parameters (nodes of
Ranvier for myelinated axons from ***Sim***), and parameters for the
binary search for thresholds (i.e., activation or block protocol,
initial upper and lower bounds on the stimulation amplitude for the
binary search, and threshold resolution for the binary search from
***Sim***). The ```launch.hoc``` file loads ```Wrapper.hoc``` which calls all NEURON
procedures. The ```launch.hoc``` file is created by the Python ```HocWriter```
class, which takes inputs of the ***Sim*** directory, ```n_sim/``` directory,
and an exception configuration. When the ```HocWriter``` class is
instantiated, it automatically loads the ```fiber_z.json``` configuration
file which contains all associated flags, parameters, and rules for
defining a fiber’s geometry and channel mechanisms in NEURON.
