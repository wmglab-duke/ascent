# Tool for Creating Dataset with ASCENT Data (SPARC's Format)
The instructions below are for creating SPARC-style datasets for uploading ASCENT data to Pennsieve. We worked with the SPARC Data Curation Team to find a dataset structure/format that is compliant with [their standards](https://github.com/fairdataihub/SODA-for-SPARC) that they apply to all datasets. Follow each step below in order.

## 1. Environment setup
**Purpose: To add the "ASCENT_DATASET_EXPORT_PATH" to your `env.json` file, which is the directory on your computer where the datasets will be saved if you use the process detailed on this page.**
   - Re-run env_setup (i.e., `python run env_setup`), OR
   - Add `"ASCENT_DATASET_EXPORT_PATH"` to your `config/system/env.json` file manually.
   - Example:
      - Dataset export path: ``"D:\\\\Documents\\\\ascent_data_shared"``
        - `\\\\` for Windows machines, OR
        - `/` for Unix-based machines (i.e., Linux,MacOS)

## 2. Choose dataset index
**Purpose: The number you choose for the "dataset_index" will be used to identify the dataset you are creating now from all other datasets you have previously made or will make in the future. The dataset index you choose is not of importance to anyone else, and is reflected nowhere in the dataset you publish. The dataset output will be saved in a sub-directory named `<dataset_index>` (e.g., `<ASCENT_DATASET_EXPORT_PATH>/0/` if you choose the "dataset_index" to be 0)**
   - Choose dataset_index for your dataset (e.g., 0, 1, 2, 3, ...)
   - Use same dataset_index value for each of your datasets for all of the following steps
   - You can do this process for multiple datasets in the same call of the script (i.e., `<dataset_indices>` in following steps which is a space separated list, e.g., "0 1 2"), so do this for each dataset you wish to create.

## 3. Create query_criteria configuration file
**Purpose: The contents of this JSON file control the scope of the data in your dataset from from the `samples/` directory. In step 6 below you can selectively remove certain data for specific n_sims, but this [query_criteria configuration file](../JSON/JSON_parameters/query_criteria.md) should have all Sample(s), Model(s), and Sim(s) to span your entire dataset.**

Template: `config/templates/dataset/query_criteria.json`
   - Create new "query_criteria" JSON file:
      - Path: `<ASCENT_DATASET_EXPORT_PATH>/config/query_criteria/<dataset_index>.json`
   - Use indices/parameters broad enough to flag all data you wish to include in the dataset
   - See template in: `config/templates/dataset/query_criteria.json`

## 4. "queried_indices_info"
**Purpose: The contents of this JSON file instruct the dataset generating tool to add additional details to the Excel file produced in Step 5. By providing paths to parameters in Sample, Model, and Sim it will be clearer in Step 6 which n_sims you wish to include or exclude from exporting.

Template: `config/templates/dataset/queried_indices_info.json`

   - Create new "queried_indices_info" file:
      - Path: `<ASCENT_DATASET_EXPORT_PATH>/config/queried_indices_info/<dataset_index>.json`
   - Add paths to the parameters you would like included in your Excel summary of Query for your results.
   - Within Sample, Model, Sim:
      - Pass a list of lists with the path to your parameters of interests.

## 5. Run build_dataset (1st of 2 times)
**Purpose: If this is the first time you are running the `build_dataset.py` script, which the program will identify because the Excel file containing queried ASCENT indices to-be-modified in Step 6 does not exist, this step creates an Excel output showing all data that matches your scope defined in the `query_criteria.json` file from Step 3.**
   - Syntax: `python run build_dataset <list of dataset_indices (e.g., 0 1 2)>`

## 6. "Modify Excel file"
**Purpose: The purpose of this step is to refine the scope of your dataset. For example, your chosen Sim might contain data for fiber diameters, pulse widths etc. that you do not wish to include in your dataset. Now is your chance to remove that data from the dataset.**
   - Modify Excel output file to govern what gets exported and how paths look in final product
   - Excel output: `<ASCENT_DATASET_EXPORT_PATH>/modify_me/<dataset_index>.xlsx`
   - Delete entries (entire rows) for Model(s)/Sim(s)/N-Sim(s) that you do not wish to include in dataset
   - If you are going to be picky about the SPARC Sam+Sub SPARC indices assigned to your ASCENT Sample Indices, Create Columns for "sam" and "sub" indices ... only must do it once for each entry you are picky about.
      - Note: there is automatic error-checking for conflicting pickiness.
      - Note: the key for which ASCENT sample_index is paired to which SPARC sub-index/sam-index is automatically
      saved to: `<ASCENT_DATASET_EXPORT_PATH>/datasets/<dataset_index>/metadata/samples_sub_sam.json`
      (note: they dictionary keys are the ASCENT sample indices)
   - Save and close Excel file.

## 7. keeps
**Purpose: The purpose of the "keeps" JSON file is to tell the program which specific files within the speceified Samples/Models/Sims/N-Sims you wish to include in your final dataset. For example, you might not want to include all files in `samples/` for the ASCENT indices you chose.**

Template: `config/templates/dataset/keeps_ascent_export_files.json`
   - Create new keeps file `<ASCENT_DATASET_EXPORT_PATH>/config/keeps/<dataset_index>.json`
      - The JSON structure mirrors the ASCENT file structure.
      - Note: keys that represent "index"-named directories (i.e., model_index, sim_index, n_sim_index) are named as such and wrapped with "<>".
      - Note: values are `true` if you wish to include the file.
      - Note: values are `false` if you do NOT wish to include the file.
      - Note: known output types (indicating there will be a list of files that match a particular regex) are wrapped in `<>` and match the keys in `config/system/regex_ascent_files.json`.
      - Note: a key can stop at the level of a directory (i.e., not file), and the entire contents will be copies over if `true`.
      - Note: a key can stop at level of a directory (i.e., not file), and NO contents will be copies over if `false`.
   - **Note to developers:** expand this template as necessary for new ASCENT intermediate files/outputs.

## 8. COMSOL clearing exceptions (optional)
**Purpose: The purpose of the "comsol_clearing_exceptions" JSON file is to tell the program which COMSOL files you wish to NOT clear the mesh/solution for in your dataset. It is important to only include meshes/solutions unless it is absolutely necessary since these files are very large (often gigabytes worth of data!)**
   - Create "comsol_clearing_exceptions" file:
      - `<ASCENT_DATASET_EXPORT_PATH>/config/comsol_clearing_exceptions/<dataset_index>.json`
      - See template in: `config/system/dataset/comsol_clearing_exceptions.json`
   - This file contains the indices for the `mesh.mph` [sample, model] or `<basis_index>.mph` [sample, model, basis_index] that you DO NOT want cleared for either mesh (`mesh.mph` or `<basis_index>.mph`) or solution (`<basis_index>.mph` ONLY).
   - COMSOL clearing will only occur if any COMSOL files have been copied over, as controlled in the preceding "keeps" step.

## 9. Run build_dataset (2nd of 2 times)
**Purpose: This finally copies over the files and clears COMSOL files as instructed previously.**

## 10. Create SODA dataset files
Use SODA to create dataset files (`subjects.xlsx`, `samples.xlsx`, `dataset_description.xlsx`, `submission.xlsx`)

## 11. Add code relevant to your dataset
  - Scripts belong in `files/code/`
  - Most importantly, include your plotting code in `files/code/plotting`
  - Contents of this folder are flexible, so this is a good place for config files specific to your dataset that are applicable across the whole dataset or the plotting code.
  - `files/code/ascent_classes/` for classes that are specific to your dataset
  - `files/code/ascent_configs/` for config files that apply broadly to your dataset (preset cuffs in `files/code/ascent_configs/cuffs/`, Sims in `files/code/ascent_configs/sims/`)
  - `files/code/ascent_metadata/` for conda/pip requirements, `samples_sub_sam.json` etc.
  - `files/code/plotting_configs/` for config files needed to run your plotting code
  - Note: make use of `files/code/ascent_metadata/samples_sub_sam.json` to convert ASCENT to SPARC indices in your code, and to relate them to any labels used in paper or elsewhere.

## 12. Use SODA to upload your dataset to Pennsieve and create manifest files
