# SPARC ACCESS: Automated Computational Cuff Electrode Stimulation Simulation

## Development Goals
* **Finished Tasks** (since September 1)
    * Implement each cuff as a sum of parts in a fully parameterized fashion
    * Add cuff specific parameters to JSON files (saved by parameters for each instance)
    * Clean up and annotate existing code for building FEM's (electrode, nerve, general model parameters)
    * Incorporate parts into model and standardize geometry indexing 
    * reading/writing data from Java, especially wrt JSON files
    * IdentifierManager
    * logic for fascicle representation from folder structures
    * Efficient saving of program states, split into higher-level nerve geometries (derived from mask data)
    * Progressbar: <a href="https://pypi.org/project/ppl/">https://pypi.org/project/ppl/</a>
    * library of generic electrode geometries and fiber information (metadata and coordinates for extracting electric potentials)
    * Add nerve to model
* **November 15**
    * Mesh and solve model (store mesh parameters in JSON)
    * Pulling out potentials and saving to file
        - API Java
        - Python code for saving potential coords; Java code for reading coords; java code for saving potentials
* **December 1**
    - Write `LaunchSim###.hoc`
    - Build simulation folder structure
* **December 15**
    * (Big ToDo)Standardized built-in data analysis
* **January 1**
    * FILTERING, SEARCHING, etc. (accessory)
    * (done) Streamline simulation indexing
    * Batching files from command line - save geom and mesh and resolve for different frequencies  (https://www.comsol.com/blogs/how-to-run-simulations-in-batch-mode-from-the-command-line/)


* **Wishlist**
    * Nerve only mode - able to build FEM and assign materials without knowing cuff design
    * Cuff only mode - anaogous to previous, but trying to finalize cuff design and don't want to deal with nerve yet
    * 1 sim - 1 fiber to be more efficient
    * Use thresholds from one fiber in nerve/fascicle to set smart bounds for thresholds of others
    * Block characterize Vm on cluster - more info that just block/no block to inform search and make less manual
    * (done) Configutations for nerve + cuff geom, configurations for waveform + material props (since function of freq) + bounds, configurations for sims?
    * Auto-converge - interpret results, built next fem, resubmit automagically
    * Characteristic nerve (fascicle are circles with location and radius)
    * Multiple contacts active at once
    * Sweep freqs, sweep PWs
    * Arbitrary waveform input
    * ...

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

## Java 1.8 Dependencies
- Maven: `org.json:json:20190722` (saved in `lib/`)
- must add to CLASSPATH: `<path-to-comsol>/COMSOL54/Multiphysics/plugins/`

## Notes for running COMSOL as standalone Java application:
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

## Setup
- IN COMSOL: Preferences -> Security -> Methods and Java Libraries -> File System Access -> All Files
- Ensure that users have write permissions to the <COMSOL installation>/plugins

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
