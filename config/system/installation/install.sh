#! /bin/bash

# confirm location
while true; do
    read -p "Have you navigated to the root of the ASCENT repository? [y/N] " yn
    case $yn in
        [Yy]* ) break;;
        [Nn]* ) echo "Please do so and re-run."; exit 1;;
        * ) echo "Please do so and re-run."; exit 1;;
    esac
done

# package installation
source ~/opt/miniconda3/etc/profile.d/conda.sh
conda create -n ascent -y
conda activate ascent
conda install -y python=3.7
python ~/opt/miniconda3/envs/ascent/bin/pip install --upgrade pip setuptools wheel
pip install pillow>=5.2.0 numpy>=1.16.4 shapely>=1.6.4 matplotlib>=3.2.1 pyclipper>=1.1.0 pygame>=1.9.6 pymunk>=5.5.0 scipy>=1.1.0 pandas>=0.25.1 openpyxl>=3.0.3 opencv-python quantiphy
conda install -y shapely

echo
echo "Installation complete."
echo
# create shortcut
while true; do
    read -p "Add ASCENT environment setup alias to '.bash_profile'? (recommended) [y/N] " yn
    case $yn in
        [Yy]* ) break;;
        [Nn]* ) echo "Not added"; exit 0;;
        * ) echo "Not added."; exit 0;;
    esac
done

echo "alias ascent_setup='source ~/opt/miniconda3/etc/profile.d/conda.sh; conda activate ascent; cd $PWD'" >> ~/.bash_profile
echo "Added. Remember to run 'ascent_setup' to use."
exit 0