echo PLEASE ENSURE THAT YOU ARE RUNNING THIS INSTALLATION SCRIPT FROM THE ROOT OF THE REPO
# TODO: CREATE CONDA ENVIRONMENT, THEN INSTALL EVERYTHING VIA INSTALL
# 
# TODO: python script for NEURON job monitoring
conda create -y ascent
conda activate ascent

conda install Pillow
conda install numpy
conda install shapely
conda install matplotlib
conda install pyclipper
conda install pygame
conda install quantiphy
conda install opencv-python
conda install -c conda-forge opencv libtiff=4.0 python=3.7 pillow
conda install pymunk
conda install scipy
conda install pandas
conda install openpyxl
conda install shutil
conda install -c conda-forge --use-local shapely
export PYTHONPATH="$PYTHONPATH:$PWD"
