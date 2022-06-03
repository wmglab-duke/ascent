Getting Started
===============

Installation
------------

Installing commercial software
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is *highly* recommended that you use a distribution of
Anaconda/Miniconda with ASCENT. However, advanced users who wish to use
another Python distribution may.

First, these software packages must be manually installed:

-  `Miniconda <https://docs.conda.io/en/latest/miniconda.html>`__/`Anaconda <https://www.anaconda.com/products/individual>`__
   We recommend that you install Miniconda (Miniconda is a stripped down
   version of Anaconda; Anaconda is optional for intermediate users). If
   you alread have an existing installation, there is no need to
   reinstall.

   -  Recommended: Select add to path
   -  Recommended: Select "Install for individual user"
   -  `https://docs.conda.io/en/latest/miniconda.html <https://docs.conda.io/en/latest/miniconda.html>`__
   -  `https://www.anaconda.com/products/individual <https://www.anaconda.com/products/individual>`__

-  `Java SE Development Kit 8
   (1.8) <https://www.oracle.com/java/technologies/javase/javase-jdk8-downloads.html>`__
   (need to register for a free account)

   -  `https://www.oracle.com/java/technologies/javase/javase-jdk8-downloads.html <https://www.oracle.com/java/technologies/javase/javase-jdk8-downloads.html>`__

-  `COMSOL 5.5 <https://www.comsol.com/product-download/5.5>`__
   (requires purchase of license; only based package needed, which
   includes the COMSOL Java API)

   -  Once COMSOL 5.5 is installed, alter 'File System Access'
      permissions via File → Preferences → Security → Methods and Java
      Libraries → File System Access → All Files.
   -  `https://www.comsol.com/product-download/5.5 <https://www.comsol.com/product-download/5.5>`__

-  `NEURON 7.6 <https://neuron.yale.edu/ftp/neuron/versions/v7.6/>`__
   (newer versions have been released, but compatibility has yet to be
   confirmed; choose appropriate installer depending on operating
   system; install auxiliary software as prompted by NEURON installer)

   -  `https://neuron.yale.edu/ftp/neuron/versions/v7.6/ <https://neuron.yale.edu/ftp/neuron/versions/v7.6/>`__
   -  If having issues with the NEURON installation, try running the
      compatibility troubleshooter.

In this stage of development, all programs/commands are run from a
command line environment on both MacOS/Linux and Windows operating
systems (Bash terminal for MacOS/Linux, Powershell for Windows). For
users less familiar with this environment and for the quickest setup, it
is suggested that the user install the package management system
`Miniconda <https://docs.conda.io/en/latest/miniconda.html>`__ or
`Anaconda <https://www.anaconda.com/products/individual>`__ (if using
MacOS, choose .pkg for ease of use).

Note that compiling NEURON files (when submitting sims) requires that
the following packages be installed and on your path (Mac and Linux
ONLY): - openmpi-2.0.0 - libreadlines.so.6

If using MacOS to run local NEURON simulations, it may be necessary to
install the Xcode Command Line Tools via ``xcode-select --install``, as
well as
`Xquartz <https://www.xquartz.org/releases/XQuartz-2.7.11.html>`__.

Users may also download a text editor or integrated development
environment (IDE) of their choosing to view/edit code (e.g.,
`Atom <https://atom.io/>`__, `Visual Studio
Code <https://code.visualstudio.com/>`__, `IntelliJ
IDEA <https://www.jetbrains.com/idea/download/>`__). For Java code, full
autocomplete functionality requires adding both the path to the COMSOL
installation ending in ``plugins`` as well as the path
``<ASCENT_PATH>/bin/json-20190722.jar`` to the list of available
libraries (usually from within the IDE’s project settings).

Installing ASCENT pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~~

1. First, download or clone the SPARC ASCENT pipeline from
   `GitHub <https://github.com/wmglab-duke/ascent>`__ to a desired
   location that will be referenced in step 3. Downloading is a much
   simpler process than cloning via Git, but does not easily allow for
   you to get the most recent updates/bug fixes, nor does it allow you
   to suggest new features/changes. If you are interested in either of
   these features, you should clone via Git rather than downloading.

   -  Downloading: Click the
      `download <https://github.com/wmglab-duke/ascent/archive/refs/heads/master.zip>`__
      button on GitHub and choose the location to which you would like
      to save. Note that you will need to extract the files, as they
      will be downloaded in a compressed format. When presented with a
      choice of compression format, ".zip" is a safe choice that most
      computers will be able to extract.
   -  Cloning via Git:

      1. You must first have an account with GitHub, and if you have
         been granted special permissions to the code repository, you
         must use the email address to which those permissions were
         granted.
      2. If you have not already done so, add an SSH key to your account
         (see instructions for
         `GitHub <https://docs.github.com/en/github/authenticating-to-github/connecting-to-github-with-ssh>`__).
         This is a required standard authentication method.
      3. In a Miniconda (or Git, for advanced users) command line
         environment, navigate to the location to where you would like
         to clone the code repository (see instructions for navigating
         the file system from the command line for `Mac or
         Linux <https://www.redhat.com/sysadmin/navigating-linux-filesystem>`__
         and
         `Windows <https://blogs.umass.edu/Techbytes/2014/11/14/file-navigation-with-windows-command-prompt/>`__).
      4. Clone the repository (see instructions for
         `GitHub <https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository>`__).
      5. For more information on using Git, check out the `official
         documentation <https://git-scm.com/doc>`__.

2. Next, install ASCENT dependencies:

   -  Windows: Open the Miniconda Powershell Prompt from the Windows
      Start Menu as Administrator, and use cd to navigate to the root
      directory of the pipeline. Then, run ``python run install``.
   -  MacOS/Linux: Open a terminal window and use cd to navigate to the
      root directory of the pipeline. Then, run ``python run install``.
   -  For advanced users using their own (non-conda) Python
      distribution:

      -  From the ascent root directory execute
         ``python run install --no-conda``
      -  From the ascent root directory execute
         ``pip install -r requirements.txt``
      -  This method is highly discouraged as newer versions of
         packages/Python could potentially break ASCENT or introduce
         unexpected bugs

After confirming that you are in the correct directory, the script will
install the required Python packages: Pillow [1], NumPy [2], Shapely
[3], Matplotlib [4], PyClipper [5], pygame [6], QuantiPhy [7], OpenCV
[8], PyMunk [9], and SciPy [10], pandas [11], and OpenPyXL [12]. It is
crucial that all of the packages are installed successfully (check for
"successfully installed" for each package). The installation script will
also create a shortcut to the newly configured ASCENT Conda
"environment" on your project path, which can be used for running the
pipeline.

3. Then, configure the environment variables. This step may be completed
   several ways, described below.

   -  Recommended Setup: Open Anaconda prompt, navigate to the ASCENT
      root directory, and execute ``python run env_setup``. You will be
      prompted for the following paths:

      -  ASCENT_COMSOL_PATH: Path to the COMSOL installation, ending in
         the directory name “Multiphysics”, as seen in the template and
         S7.
      -  ASCENT_JDK_PATH: Path to the JDK 1.8 installation, ending in
         ``bin``, as seen in the template and S7. Hint: This is the
         correct path if the directory contains many executables (for
         Windows: java.exe, etc.; MacOS/Linux: java, etc.).
      -  ASCENT_PROJECT_PATH: Path to the root directory of the
         pipeline, as chosen for step 1.
      -  ASCENT_NSIM_EXPORT_PATH: Path to the export location for NEURON
         “simulation” directories. This path only depends on on the
         user's desired file system organization.

   -  Manual Setup: Copy the file ``config/templates/env.json`` into
      ``config/system/env.json`` (new file). This file holds important
      paths for software used by the pipeline (see env.json in S6 and
      S7). Then, edit each of the four values as specified below. Use
      ``\\`` in Windows and ``/`` in MacOS/Linux operating systems. Note
      that the file separators are operating system dependent, so even
      if you installed in step 2 with Unix-like command environment on a
      Windows machine (e.g., using `Git
      Bash <https://gitforwindows.org/>`__,
      `Cygwin <https://www.cygwin.com/>`__, or a VM with
      `Ubuntu <https://ubuntu.com/>`__), you will still need to choose
      the proper file separator for Windows, i.e., ``\\``). See example
      env.json files for both MacOS and Windows (`S8
      Text <S8-JSON-file-parameter-guide>`__).
   -  Automatic setup: Upon the initiation of your first run, you will
      be prompted to enter the above four paths if you did not choose to
      complete the manual setup. Enter them as prompted, following the
      guidelines detailed above and exemplified in
      `S7 <S7-JSON-configuration-files>`__. Note that you may at any
      time update paths with ``python run env_setup`` to rewrite this
      file if the information should change.

4. Before the first time you run the pipeline, you must open the COMSOL
   Server and log in with a username and password of your choosing
   (arbitrary and not needed thereafter). This can be done by navigating
   to the bin/ directory in the COMSOL installation and running
   ``comsolmphserver`` (Windows) or ``./comsol server`` (MacOS/Linux).

References
~~~~~~~~~~

1.  Clark A. Pillow: a modern fork of PIL — Pillow v2.3.0 (PIL fork)
    [Internet]. 2020 [cited 2020 Apr 20]. Available from:
    `https://pillow.readthedocs.io/en/2.3.0/ <https://pillow.readthedocs.io/en/2.3.0/>`__
2.  Oliphant TE. A Guide to NumPy [Internet]. Trelgol Publishing; 2006.
    Available from:
    `https://books.google.com/books?id=fKulSgAACAAJ <https://books.google.com/books?id=fKulSgAACAAJ>`__
3.  Gillies S. Shapely · PyPI [Internet]. 2019 [cited 2020 Apr 20].
    Available from:
    `https://pypi.org/project/Shapely/ <https://pypi.org/project/Shapely/>`__
4.  Hunter JD. Matplotlib: A 2D Graphics Environment. Comput Sci Eng.
    2007 May;9(3):90–5.
5.  Johnson A, Chalton M, Treyer L, Ratajc G. pyclipper · PyPI
    [Internet]. 2019 [cited 2020 Apr 20]. Available from:
    `https://pypi.org/project/pyclipper/ <https://pypi.org/project/pyclipper/>`__
6.  Shinners P. Pygame Intro — pygame v2.0.0.dev5 documentation
    [Internet]. [cited 2020 Apr 20]. Available from:
    `https://www.pygame.org/docs/tut/PygameIntro.html <https://www.pygame.org/docs/tut/PygameIntro.html>`__
7.  Kundert K. QuantiPhy: Physical Quantities — quantiphy 2.10.0
    documentation [Internet]. 2020 [cited 2020 Apr 20]. Available from:
    `https://quantiphy.readthedocs.io/en/stable/ <https://quantiphy.readthedocs.io/en/stable/>`__
8.  Bradski G, Daebler A. Learning OpenCV. Computer vision with OpenCV
    library. 2008 Jan 1;222–64.
9.  Blomqvist V. pymunk · PyPI [Internet]. 2019 [cited 2020 Apr 20].
    Available from:
    `https://pypi.org/project/pymunk/ <https://pypi.org/project/pymunk/>`__
10. Virtanen P, Gommers R, Oliphant TE, Haberland M, Reddy T, Cournapeau
    D, et al. SciPy 1.0: fundamental algorithms for scientific computing
    in Python. Nat Methods [Internet]. 2020;17(3):261–72. Available
    from:
    `https://doi.org/10.1038/s41592-019-0686-2 <https://doi.org/10.1038/s41592-019-0686-2>`__
11. The pandas development team. pandas-dev/pandas: Pandas [Internet].
    Zenodo; 2020. Available from:
    `https://doi.org/10.5281/zenodo.3509134 <https://doi.org/10.5281/zenodo.3509134>`__
12. Gazoni E, Clark C. openpyxl - A Python library to read/write Excel
    2010 xlsx/xlsm files [Internet]. 2020. Available from:
    `https://openpyxl.readthedocs.io/en/stable/ <https://openpyxl.readthedocs.io/en/stable/>`__

Metadata required to model an in vivo experiment using the ASCENT pipeline
--------------------------------------------------------------------------

Note: All metadata required for the `tutorial run <#tutorial-run>`__ are
provided with ASCENT.

1. Detailed specifications / dimensions of the stimulating cuff
   electrode.

2. Transverse cross section of the nerve where the cuff is placed,
   stained to visualize the different tissue types (e.g., using Masson’s
   trichrome), with a scale bar (`Fig
   2 <https://doi.org/10.1371/journal.pcbi.1009285.g002>`__ and `S11
   Text <S11-Morphology-files>`__) or known scale (micrometers/pixel).
   Different possible sources for defining the nerve sample morphology
   include:

   a. For best specificity, the nerve would be sampled from the specific
   animal used in the experiment being modeled. In this case, two colors
   of tissue dye may be used on the ventral and medial aspects of the
   nerve to maintain orientation information.

   b. Otherwise, a sample from another animal of the same species could
   be used at the correct nerve level.

   c. If multiple samples from other animals are available, they could
   be used to generate a representative nerve model, knowing the range
   of morphological metrics across individuals using the
   ``scripts/mock_morphology_generator.py`` script (`S12
   Text <S12-Python-MockSample-class-for-creating-binary-masks-of-nerve-morphology>`__).

   d. Lastly, published data could be used.

3. Orientation and rotation of the cuff on the nerve (e.g., cuff closure
   on the ventral side of the nerve).

4. Fiber diameters

   a. Distributions of fiber diameters may be obtained from literature;
   otherwise, detailed electromicroscopic studies are required.

   b. The fiber diameters found in the target nerve that will be
   simulated in NEURON. All diameters or a subset of diameters may be of
   interest.

   c. Each fiber diameter of interest can be simulated for each fiber
   location of interest, or specific fiber diameters can be simulated in
   specific locations.

5. Approximate tissue or fluids surrounding the nerve and cuff (e.g.,
   muscle, fat, or saline).

6. Stimulation waveforms, pulse widths, and other parameters of the
   electrical signal.

7. If comparing to neural recordings: distance between the stimulation
   and recording cuffs.

8. If comparing to functional recordings (e.g., EMG): distance from the
   stimulation cuff to the location where the nerve inserts into the
   muscle.

Tutorial Run
------------

*How to run the ASCENT pipeline, after completing the initial setup.*

The user provides binary mask inputs for the nerve and saves **Sample**
(i.e., ``sample.json``), **Model(s)** (i.e., ``model.json``), and
**Sim(s)** (i.e., ``sim.json``) JSON configurations in directories,
relative to the project path defined in ``config/system/env.json``. The
directory names must use indices that are consistent with the indices of
**Sample**, **Model(s)**, and **Sim(s)** defined in **Run**.

1. **Masks:** User populates ``input/<NAME>/`` (e.g., “Rat1-1”, which
   must match “sample” parameter in **Sample**) with binary masks of
   neural tissue boundaries using either:

   a. Segmented histology (`S11 Text <S11-Morphology-files>`__ and `Fig
   2 <https://doi.org/10.1371/journal.pcbi.1009285.g002>`__), or

   b. Running the ``mock_morphology_generator.py`` script (`S12
   Text <S12-Python-MockSample-class-for-creating-binary-masks-of-nerve-morphology>`__).

   ::

       i.  Copy `mock_sample.json` from `config/templates/` to
            `config/user/mock_samples/` as `<mock_sample_index>.json`
            and update file contents, including the “NAME” parameter
            used to construct the destination path for the output binary
            masks, which serve as inputs to the pipeline.

       ii.  Call `“python run mock_morphology_generator
            <mock_sample_index>”`.

       iii.  The program saves a copy of the user’s `mock_sample.json` and
            binary masks in `input/<NAME>/`.

2. **For one Sample:** User copies ``sample.json`` from
   ``config/templates/`` to ``samples/<sample_index>/`` as
   ``sample.json`` and edits its contents to define the processing of
   binary masks to generate the two-dimensional cross section geometry
   of the nerve in the FEM. In particular, change “sample” to match
   ``<NAME>``, the ``“scale_bar_length”`` parameter for ``s.tif`` (i.e.,
   length in microns of your scale bar, which is oriented horizontally),
   and ``“mask_input”`` in **Sample** accordingly (`S8
   Text <S8-JSON-file-parameter-guide>`__). You have now created the
   directory for your first sample: ``sample #<sample_index>``. Note: in
   lieu of a scale bar image, the user may optionally specify the
   microns/pixel ratio for the sample mask(s).

3. **For each Model:** User copies ``model.json`` from
   ``config/templates/`` to
   ``samples/<sample_index>/models/<model_index>/`` as ``model.json``
   and edits its contents to define the three dimensional FEM.

   a. **Preset:** User defines a new “preset” cuff JSON file, which
   contains instructions for creating their cuff electrode, and saves it
   as ``config/system/cuffs/<preset_str>.json``.

   b. The ``<preset_str>.json`` file name must be assigned to the
   “preset” parameter in **Model** (`S8
   Text <S8-JSON-file-parameter-guide>`__).

4. **For each Sim:** User copies ``sim.json`` from ``config/templates/``
   to ``config/user/sims/`` as ``<sim_index>.json`` and edits its
   contents to inform the NEURON simulations (`S8
   Text <S8-JSON-file-parameter-guide>`__).

5. **Run:** User copies ``run.json`` from ``config/templates/`` to
   ``config/user/runs/`` as ``<run_index>.json`` and edits the indices
   for the created **Sample**, **Model(s)**, and **Sim(s)**
   configurations (`S8 Text <S8-JSON-file-parameter-guide>`__).

6. The pipeline is run from the project path (i.e., the path to the root
   of the ASCENT pipeline, which is defined in
   ``config/system/env.json``) with the command
   ``“python run pipeline <run indices>”``, where ``<run indices>`` is a
   list of space-separated **Run** indices (if multiple **Sample**
   indices, one **Run** for each). The pipeline outputs ready-to-submit
   NEURON simulations and associated **Run file(s)** to the
   ``“ASCENT_NSIM_EXPORT_PATH”`` directory as defined in
   ``config/system/env.json`` (`S8
   Text <S8-JSON-file-parameter-guide>`__). NEURON simulations are run
   locally or submitted to a computer cluster with the command
   ``“python submit.py <run indices>”`` from the export directory.

Task given to beta testers
~~~~~~~~~~~~~~~~~~~~~~~~~~

We sent the pipeline code, manuscript, and the following task to beta
testers (both within our lab at Duke and externally). Following this
task and verifying the threshold value is a suitable way to familiarize
yourself with the ASCENT code and documentation.

We provided segmented histology of a rat cervical vagus nerve
(``examples/beta_task/``). Please simulate activation thresholds in
response to a charge balanced, biphasic pulse (PW1 = 100 μs, interphase
gap of 100 μs, PW2 = 400 μs) using Purdue’s bipolar cuff design.

-  MRG 8.7 μm diameter fibers

-  Fibers placed in nerve cross section using a 6 spoke wheel with 2
   fibers per spoke

-  Custom material for surrounding medium with isotropic conductivity
   1/20 [S/m]

After your thresholds have been computed, build a heatmap for the
threshold at each fiber location using the example script:
``examples/analysis/heatmap_monofasc.py``.

Through this exercise, you will:

-  Place and name binary masks of the nerve morphology in the proper
   directories

   -  Binary masks provided

-  Define and assign a custom material

-  Build and solve a finite element model

-  Define placement of fibers in the nerve cross section

-  Parameterize your custom stimulation waveform

-  Simulate activation thresholds for a specific fiber model by
   submitting NEURON simulations locally or to a computer cluster

-  View and analyze your data

   -  Plot samples with color-coded fiber (x,y)-coordinates

   -  Heatmap of fiber thresholds

For the following exercise, we ask that you please attempt to accomplish
the prescribed modeling tasks with the paper and associated supplemental
documentation as your primary reference.

Check: Threshold for inner0_fiber0 (``thresh_inner0_fiber0.dat``) should
be -0.028732 mA

We provided **Sample**, **Model**, and **Sim** JSON files for the
solution in ``examples/beta_task/``.
