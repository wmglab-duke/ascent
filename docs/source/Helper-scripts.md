# Helper Scripts

We provide scripts to help users efficiently manage data created by ASCENT. Run all of these scripts from the directory
to which you installed ASCENT (i.e., `"ASCENT_PROJECT_PATH"` as defined in `config/system/env.json`).
For more usage information, including optional arguments, see [Command-Line Arguments](command_line_args).

## `scripts/import_n_sims.py`
To import NEURON simulation outputs (e.g., thresholds, recordings of V<sub>m</sub>) from your `ASCENT_NSIM_EXPORT_PATH`
(i.e., `<"ASCENT_NSIM_EXPORT_PATH" as defined in env.json>/n_sims/<concatenated indices as
sample_model_sim_nsim>/data/outputs/`) into the native file structure
(see ["ASCENT data hierarchy"](S3-ASCENT-data-hierarchy), `samples/<sample_index>/models/<model_index>/sims/<sim_index>/n_sims/<n_sim_index>/data/outputs/`)
run this script from your `"ASCENT_PROJECT_PATH"`.

`python run import_n_sims <list of run indices>`

The script will load each listed Run configuration file from `config/user/runs/<run_index>.json` to determine for which
Sample, Model(s), and Sim(s) to import the NEURON simulation data. This script will check for any missing thresholds and skip that import if any are found. Override this by passing the flag `--force`. To delete n_sim folders from your output directory after importing, pass the flag `--delete-nsims`. For more information, see [Command-Line Arguments](command_line_args).

## `scripts/clean_samples.py`
If you would like to remove all contents for a single sample (i.e., `samples/<sample_index>/`) EXCEPT a list of files
(e.g., `sample.json`, `model.json`) or EXCEPT a certain file format (e.g., all files ending `.mph`), use this script.
Run this script from your `"ASCENT_PROJECT_PATH"`. Files to keep are specified within the python script.

`python run clean_samples <list of sample indices>`

## `scripts/tidy_samples.py`
If you would like to remove ONLY CERTAIN FILES for a single sample (i.e., `samples/<sample_index>/`), use this script.
 This script is useful for removing logs, runtimes, special,
 and *.bat or *.sh scripts. Run this script from your `"ASCENT_PROJECT_PATH"`. Files to remove are specified within the python script.

`python run tidy_samples <list of sample indices>`
