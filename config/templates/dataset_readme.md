# Example README.txt
- From: [(ASCENT Dataset for Blanz et al., 2023)](https://doi.org/10.26275/hybx-ggbt)
- The purpose of the README.txt file is to communicate the contents of the dataset to someone else succinctly.
- Required for all SPARC datasets published on Pennsieve.

The files in primary/sub-<>/sam-<>-sub-<>/samples/<>/ephys/ contain data from stimulating the nerve for this specific subject/sample combination, but are measurements (i.e., EMG, ECG) from the scope of the whole animal. The data is also published in the associated dataset: https://doi.org/10.26275/efbj-8evl

The files in primary/sub-<>/sam-<>-sub-<>/samples/<>/slides/0/0/ are mask of histology from the nerve site of stimulation for this specific subject/sample combination. The data is also published in the associated dataset: https://doi.org/10.26275/efbj-8evl

Run the plotting scripts in the dataset with ASCENT v1.1.0 (repository: https://github.com/wmglab-duke/ascent; documentation: https://wmglab-duke-ascent.readthedocs.io/en/latest/). If you have not already, clone the ASCENT repository (see installation instructions in the documentation) and checkout release v1.1.0.
The required Python packages are provided in files/code/metadata/<conda and pip>_requirements.txt. Install with <pip and conda> install <conda and pip>_requirements.txt.

ASCENT sample.py, simulation.py, and query.py classes, which have minor changes necessary for recreating the heatmaps in the associated paper, are included in files/code/ascent_classes/. You can replace the classes in your ASCENT installation’s src/core/ directory.

In your ASCENT conda environment, set files/code/ as your working directory. Run onset_saturation.py (run for bimodal_override = 1 AND 0) which outputs files to packaged_data/. Then run summary_imthera.py which loads the data from packaged_data/.

To create heatmaps, copy the samples into your ASCENT installation's samples/ folder:
- primary/sub-<>/sam-<>-sub-<>/samples/ --> <ASCENT_INSTALLATION_PATH>/samples/ for Samples [2000, 2003, 2004, 2005, 2014, 2015]

The link between SPARC's indices for "sub" (i.e., sub-1 ... sub-6) and "sam" (i.e., sam-0) are linked to the ASCENT Sample Config index
(i.e., 2000, 2003, 2004, 2005, 2014, 2015) and the Animal # used in the associated paper in files/code/metadata/samples_sub_sam.json. Each ASCENT Sample Config Index
is a key in the dictionary, with values of "sub", "sam", and "animal".

Figures created by heatmaps.py and heatmaps_fixed_amp.py will need adjusting based on your screen (use plt.subplots_adjust(top=<>, bottom=<>, left=<>, right=<>, hspace=<>, wspace=<>))

The ASCENT Sim Config index used in these simulations (i.e., 1071.json) is in files/code/ascent_configs/sims/

The ASCENT Preset Cuff Config used in these FEMs (i.e., ImThera_flip_100.json) is in files/code/ascent_configs/cuffs/

# Curator's Notes
- Curator's Notes are included with every published SPARC dataset on Pennsieve.
- Curator's Notes must have the following sections.
- Draft the Curator's Notes for the Dataset SPARC Curation Team to reduce the number of iterations.

## Experimental Design:
- Brief methods description.

## Completeness:
- Is this dataset is part of a larger study? If so, what is the larger study?

## Subjects & Samples:
- High level description of subjects and samples (in SPARC language).

## Primary vs derivative data:
- Data in the primary and derivative folders are divided by subject number (listed in subject file), then sample number (listed in sample file).
- The **primary folder** contains <what?> (loaded and analyzed by Python/MATLAB? scripts in the "code" folder).
- The **derivative folder** contains <what?>

## Code Availability:
- In the "code" folder. What does the code do? What are the dependencies? What is the order of execution? Filepaths in the code need to be set to work as-is, in-place in the dataset.

# Example Curators Notes
- From: [(ASCENT Dataset for Blanz et al., 2023)](https://doi.org/10.26275/hybx-ggbt)

## Experimental Design:
- This is a computational study.

## Completeness:
- This dataset is complete.

## Subjects & Samples:
- Only virtual subjects were used in this study. We modeled six right cervical pig vagus nerves. Histology and experimental data obtained from miniature swine subjects originate from https://doi.org/10.26275/efbj-8evl.

## Primary vs derivative data:
- Primary data folder contains three data elements.

### Nerve morphology:
- The files in primary/sub-<*>/sam-<*>-sub-<*>/samples/<*>/slides/0/0/masks/ are the histology and segmentations of the vagus nerve morphology at the site of stimulation for this specific subject/sample. The data are also published in the associated: https://doi.org/10.26275/efbj-8evl.

### Model inputs and outputs:
- The files in primary/sub-<*>/sam-<*>-sub-<*>/samples/<*>/ are ASCENT input configuration files (i.e., sample.json, models/<*>/model.json) and outputs (i.e., individual fiber activation thresholds models/<*>/sims/<*>/n_sims/<*>/data/outputs/thresh_inner<*>_fiber<*>.dat). Additionally, the files in primary/sub-<*>/sam-<*>-sub-<*>/samples/<*>/ contain key intermediate files created by ASCENT, including the extracellular potentials applied to the fiber models (models/<*>/sims/<*>/n_sims/<*>/data/inputs/inner<*>_fiber<*>.dat) and the stimulation waveform (models/<*>/sims/<*>/n_sims/<*>/data/inputs/waveform.dat).

### In vivo recordings for model validation:
- The files in primary/sub-<*>/sam-<*>-sub-<*>/samples/<*>/ephys/ contain electrophysiological recordings (i.e., EMG, EKG) in response to vagus nerve stimulation for this specific subject/sample combination. The data are also published in the associated: https://doi.org/10.26275/efbj-8evl.

## Code Availability:
- Run the plotting scripts in the dataset using ASCENT v1.1.0 ([repository](https://github.com/wmglab-duke/ascent); [documentation](https://wmglab-duke-ascent.readthedocs.io/en/latest/)): see README.txt for details.
