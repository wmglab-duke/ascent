# Troubleshooting Guide

## General Troubleshooting Steps
- Check your geometry (ascent/samples/sample_index/models/model_index/debug_geom.mph)
- Check your sample (ascent/samples/sample_index/slides/cassette_index/slide_index/masks)

## Installation Issues
- NEURON
    - Issue: Sometimes NEURON installation will complete but NEURON will not be installed
    - Solution: Run the installer in Windows 8 compatibility mode

## Pipeline Issues
- Sample
    - Issue: Small white pixel islands cause the pipeline to fail, or the pipeline does not fail but very small elements are present as fascicles that reflect segmentation errors
    - Solution: increase value of image_preprocessing>object_removal_area in sample.json
- Model
    - Issue: fascicle borders appear ragged/wavy in model geometry
    - Solutions:
        - Increase inner_interp_tol and/or outer_interp_tol in  sample.json (depending on whether the Issue exists for outers or inners)
        - If your mask is very pixelated, increase smoothing>fascicle distance in sample.json
    - issue: The pipeline solves one basis, then errors.
    - solution: In COMSOL, disable automatic saving of recovery files.

## NEURON Issues
- Issue: Compiling NEURON files with `python submit.py` results in an error, `mpicc: command not found`
- Solution: Install open-mpi 2.0 and add to path

## Python Issues
- Issue: python output prints out of order with java output
- Solution: pass the -u flag (i.e. python -u run pipeline <run indices>), which turns off output buffering
