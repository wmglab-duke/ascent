# Tool for Creating Dataset with ASCENT Data (SPARC Format)

1. "Setup"
   - Re-run env_setup (i.e., "python run env_setup"), OR
   - Add "ASCENT_DATASET_EXPORT_PATH" to your config/system/env.json file
   - Example:
      - Dataset export path: "D:\\\\Documents\\\\ascent_data_shared"
        - \\\\ for Windows machines, OR
        - / for Unix-based machines (i.e., Linux, MacOS)
2. "dataset_index"
   - Choose dataset_index for your dataset (e.g., 0, 1, 2, 3, ...)
    - Use same index value(s) in all the following steps
    - You can do this process for multiple datasets in the same call of the script (i.e., \<dataset_indices\> in following steps which is a space separated list, e.g., "0 1 2"), so do this for each dataset you wish to create
3. "query_criteria"
   - Create new "query_criteria" file:
    - Path: \<ASCENT_DATASET_EXPORT_PATH\>/config/query_criteria/\<dataset_index\>.json
   - Use indices/parameters broad enough to flag all data you wish to include in the dataset
   - See template in config/templates/query_criteria.json
4. "queried_indices_info"
   - Create new "queried_indices_info" file:
    - Path: \<ASCENT_DATASET_EXPORT_PATH\>/config/queried_indices_info/\<dataset_index\>.json
   - Add paths to the parameters you would like included in your Excel summary of Query for your results
   - Within Sample, Model, Sim:
      - Pass a list of lists with path to your parameters of interests
   - See template in: config/templates/queried_indices_info.json
5. "Run this script #1" (1st of 2 times)
   - Command:
      - python run build_dataset \<dataset_indices\>
   - This command queries your ASCENT directory to figure out what data matches your "query_criteria", and saves the contents to "Excel output" (see next step)
6. "Modify Excel file"
   - Modify Excel output to govern what gets exported and how paths look in final product
   - Excel output:
      - \<ASCENT_DATASET_EXPORT_PATH\>/modify_me/\<dataset_index\>.xlsx
   - Delete entries (entire rows) for Model(s)/Sim(s)/N-Sim(s) that you do not wish to include in dataset
   - If you are going to be picky about the SPARC Sam+Sub SPARC indices assigned to your ASCENT Sample Indices, Create Columns for "sam" and "sub" indices ... only must do it once for each entry you are picky about.
      - Note: there is automatic error-checking for conflicting pickiness.
      - Note: the key for which ASCENT sample_index is paired to which SPARC sub-index/sam-index is automatically
      saved to: \<ASCENT_DATASET_EXPORT_PATH\>/datasets/\<dataset_index\>/metadata/samples_sub_sam.json
      (keys are ASCENT samples)
   - Save and close Excel file.
7. "keeps"
   - Create new keeps file \<ASCENT_DATASET_EXPORT_PATH\>/config/keeps/\<dataset_index\>.json
      - The JSON strx mirrors the ASCENT file strx
      - Note: keys that represent "index"-named directories (i.e., model_index, sim_index, n_sim_index) are named as such and wrapped with "\<\>"
      - Note: values are true if you wish to include the file
      - Note: values are false if you do NOT wish to include the file
      - Note: known output types (indicating there will be a list of files that match a particular regex) are wrapped in "\<\>" and match the keys in config/system/regex_ascent_files.json
      - Note: key can stop at level of a directory (i.e., not file), and the entire contents will be copies over if true
      - Note: key can stop at level of a directory (i.e., not file), and NO contents will be copies over if false
      - See recommended template in config/templates/keeps_ascent_export_files.json
      - Note to developers: expand this as necessary for new ASCENT intermediate files/outputs
8. "comsol_clearing_exceptions" (optional)
    - Create "comsol_clearing_exceptions" file:
      - \<ASCENT_DATASET_EXPORT_PATH\>/config/comsol_clearing_exceptions/\<dataset_index\>.json
      - See template in config/system/comsol_clearing_exceptions.json
    - This file contains the indices for the mesh.mph [sample, model] or \<basis_index\>.mph [sample, model, basis_index] that you DO NOT want cleared for either mesh (mesh.mph or \<basis_index\>.mph) or solution (\<basis_index\>.mph ONLY)
    - COMSOL clearing will only occur if any COMSOL files have been copied over, as controlled in the preceding "keeps" step
9. "Run this script #2" (2nd of 2 times)
    - This finally copies over the files and clears COMSOL files as instructed in previous step
10. "SODA"
    - Use SODA to create dataset files (subjects.xlsx, samples.xlsx, dataset_description.xlsx, submission.xlsx)
    - Template for responses here: \<link forthcoming\>
      - You will likely want to iterate on your responses with your advisor.
11. "Add plotting/analysis scripts"
    - Scripts belong in files/code/
    - Contents of this folder are flexible, so this is a good place for config files specific to your dataset that are applicable across the whole dataset or the plotting code alone.
    - files/code/ascent_classes/ for classes that are specific to your dataset
    - files/code/ascent_configs/ for config files that apply broadly to your dataset (preset cuffs in "files/code/ascent_configs/cuffs/", Sims in "files/code/ascent_configs/sims/")
    - files/code/ascent_metadata/ for conda/pip requirements, samples_sub_sam.json, etc.
    - files/code/plotting_configs/ for config files needed to run your plotting code
    - Note: make use of files/code/ascent_metadata/samples_sub_sam.json to convert ASCENT to SPARC indices, and to relate them to any labels used in paper or elsewhere.
12. Use SODA to upload dataset to Pennsieve and create manifest files
