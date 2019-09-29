# SPARC ACCESS: Automated Computational Cuff Electrode Stimulation Simulation

## BIG NOTES FOR RUNNING AS JAVA STANDALONE:
* `javac` from the Java 1.8 SDK.
* `java` from `<COMSOL INSTALLATION>/java/maci64/jre/Contents/Home/bin/java`
* In separate terminal, run `./comsol server`
* In main Java file being ran, MUST run `ModelUtil.connect("localhost, 2036)`, `ModelUtil.initStandalone(true)`,
ALL OTHER OPERATIONS, then finally `ModelUtil.disconnect()`
* Example commands starting at the project root (facilitated by Runner.handoff):
```
cd src
/Library/Java/JavaVirtualMachines/jdk1.8.0_221.jdk/Contents/Home/bin/javac -classpath /Users/jakecariello/Box/Documents/Pipeline/access/lib/json-20190722.jar:/Applications/COMSOL54/Multiphysics/plugins/* model/*.java
/Applications/COMSOL54/Multiphysics/java/maci64/jre/Contents/Home/bin/java -cp .:$(echo /Applications/COMSOL54/Multiphysics/plugins/*.jar | tr ' ' ':'):/Users/jakecariello/Box/Documents/Pipeline/access/lib/json-20190722.jar model/FEMBuilder
cd ..
```

## Future Development Goals
*  **Monday, Sept. 16, 2019** COMSOL-interfacing Java code to build models
    * Eric
        - (**done**)add cuff specific parameters to master
        - (**done**) clean up and annotate existing MATLAB code for building FEM's (electrode, nerve, general model parameters)
        - (**done**)Fix ImThera, make copy of FEM Builder and work from that
        - (**done**)Fix LivaNova, make copy of FEM Builder and work from that
        - Add nerve to FEMBuilder
        - Mesh and solve FEMBuilder (store mesh parameters in JSON)
    * Jake
        - (**done**) now incorporate into FEMBuilder) standardize geometry indexing 
        - (**done**) reading/writing data from Java, especially wrt JSON files
        - CIM added to FEMBuilder 
        - Pulling out potentials and saving to file
            -API Java
            -Python code for saving potential coords; Java code for reading coords; java code for saving potentials
        - (waiting on Eric) general model geometry validation, particularly wrt electrodes (specific to each)

    * Both
        - logic for fascicle representation from folder structures
* **Friday, Sept. 20, 2019** Extracting potentials from solved models, saving to file, and successfully loading for
use in Python (for Both)
* **Oct. 1** NEURON-interfacing Python code (to interface with preexisting NEURON code written in Hoc) to build launch
files for simulation (for Both)
    - Write `LaunchSim###.hoc`
    - Build simulation folder structure
    - Streamline simulation indexing
    - Upload to Cluster and confirm successful simulation
* **Nov. 1** 
    * Efficient saving of program states, split into higher-level nerve geometries (derived from mask data)
and fiber information (metadata and coordinates for extracting electric potentials)
    * Standardized built-in data analysis
    * GUI - prompt user to input parameters based on previous inputs. Save to JSON.
* **Dec. 1**
    * FILTERING, SEARCHING, etc. (accessory)
* Possible add-ons
    * Investigate methods of streamlining/standardizing interface with cluster computing service
    * Implement best-fit bounding ellipse for CuffInputMode (written to electrode_input.json).
    * pretty progressbar: <a href="https://pypi.org/project/ppl/">https://pypi.org/project/ppl/</a>
    * library of generic electrode geometries
    * port NEURON code to Python?
    * Batching files from command line - save geom and mesh and resolve for different frequencies: https://www.comsol.com/blogs/how-to-run-simulations-in-batch-mode-from-the-command-line/

## Python 3.7 Dependencies (non-builtin)
- `numpy`
- `Pillow`
- `cv2` (opencv-python)
- `matplotlib`
- `shapely`
- `pyclipper`
- `pymunk`
- `pygame`
- `shutil`
- `json`

## Java 1.8 Dependencies (figure out streamlining?)
- Maven: `com.googlecode.json-simple:json-simple:1.1`
- must add to CLASSPATH: `<path-to-comsol>/COMSOL54/Multiphysics/plugins/`
- if using IntelliJ, ensure presence of line in `access.iml`: `<component name="NewModuleRootManager" inherit-compiler-output="true">`

## Setup
- IN COMSOL: Preferences -> Security -> Methods and Java Libraries -> File System Access -> All Files
- Ensure that users have write permissions to the <COMSOL installation>/plugins
- Add com.comsol.accessutils_1.0.0.jar to <COMSOL installation>\bin\comsolpath.txt, might need to adjust security settings to do this

## Source images
The user must provide 3 types of files that will be used to construct the data filesystem. In addition to the type
designation (a single letter, seen in filename specifications below), 3 pieces of data must be included:

1. `[SAMPLE]` – The sample name. Must be unique and not contain any underscores.im

2. `[CASSETTE]` – If a multi-slide sample is being analyzed, use a consistent system of uniquely identifying cassettes
used for embedding and slicing. In the (probably very common) cases that either one unnamed cassette was used or a
single-slide sample is being analyzed (via extrusion?), then default to a cassette name of "`0`". The essential aspect
of this naming system is that there be a **unique** and **consistent** identifier for each cassette.

3. `[NUMBER]` – For multi-slide samples, use a numbering system such that the linear order of samples is represented by
the order of numbers. In addition, the should be a unique slide for each cassette/number pairing. As with cassettes, 
default to the number "`0`" if numbering **within a sample** is not needed. Note that his does not pertain to the likely
scenario that individual samples have been numbered according to an arbitrary system; this information is not relevant
to SPARCpy and can thus be included in the **sample name** if desired.

Below is a description of the specific filename formatting for each of the 3 required file types. Note that, for all
formatting, there must be at least 1 underscore where indicated, but more than 1 is allowed and ignored. Each file type
description is accompanied by an example of what that image may look like (at lower resolution for efficiency).

1. Raw image of slide
    - form: `[SAMPLE]_[CASSETTE]_[NUMBER]_r.tif`
    - type: Though `.tif` is indicated above filename, this is arbitrary for now.
    - <a href="https://gitlab.oit.duke.edu/edm23/sparcpy/raw/master/examples/images/masks/raw.jpg" target="_blank">example</a>
2. Compiled fascicles binary mask
    - form: `[SAMPLE]_[CASSETTE]_[NUMBER]_f.tif`
    - type: Only `.tif` allowed for now.
    - <a href="https://gitlab.oit.duke.edu/edm23/sparcpy/raw/master/examples/images/masks/fascicle_normal.jpg" target="_blank">one-to-one</a> or containing <a href="https://gitlab.oit.duke.edu/edm23/sparcpy/raw/master/examples/images/masks/fascicle_peanut.jpg" target="_blank">peanut fascicles</a>
3. Individual fascicles binary masks
    - forms: `[SAMPLE]_[CASSETTE]_[NUMBER]_i.tif` (inner) or `[SAMPLE]_[CASSETTE]_[NUMBER]_o.tif` (outer)
    - type: Only `.tif` allowed for now.
    - notes: in place of a single compiled fascicles mask. either both `_i` and `_o` must be provided or only one is provided (a scale for perineurium thickness with appropriate direction must be provided at a later point)
4. Nerve binary mask
    - form: `[SAMPLE]_[CASSETTE]_[NUMBER]_n.tif`
    - type: Only `.tif` allowed for now.
    - <a href="https://gitlab.oit.duke.edu/edm23/sparcpy/raw/master/examples/images/masks/nerve.jpg" target="_blank">example</a>
5. Scale bar mask
    - form: `[SAMPLE]_[CASSETTE]_[NUMBER]_s.tif`
    - type: Only `.tif` allowed for now.
    - <a href="https://gitlab.oit.duke.edu/edm23/sparcpy/raw/master/examples/images/masks/scalebar.jpg" target="_blank">example</a>

An example for a grouping of four images for a slide might be:
- `MyPig4_UpperCas_12_r.tif`
- `MyPig4_UpperCas_12_f.tif`
- `MyPig4_UpperCas_12_n.tif`
- `MyPig4_UpperCas_12_s.tif`
