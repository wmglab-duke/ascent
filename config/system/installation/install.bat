echo PLEASE ENSURE THAT YOU ARE RUNNING THIS INSTALLATION SCRIPT FROM THE ROOT OF THE REPO
# TODO: CREATE CONDA ENVIRONMENT, THEN INSTALL EVERYTHING VIA INSTALL
# 
# TODO: python script for NEURON job monitoring
pip install --user pip
pip install --user Pillow
pip install --user numpy
pip install --user shapely
pip install --user matplotlib
pip install --user pyclipper
pip install --user pygame
pip install --user quantiphy
pip install --user opencv-python
pip install --user pymunk
pip install --user scipy
pip install --user pandas
pip install --user openpyxl
pip install --user shutil
conda install -c conda-forge --use-local shapely
conda install -c conda-forge opencv libtiff=4.0 python=3.7 pillow
export PYTHONPATH="$PYTHONPATH:$PWD"
