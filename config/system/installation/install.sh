#! /bin/bash

# set up conda for this environment, choosing between Linux/macOS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    CONDA_SETUP_SCRIPT=~/miniconda3/etc/profile.d/conda.sh
    CONDA_BIN=~/miniconda3/envs/ascent/bin
else
    # macOS
    CONDA_SETUP_SCRIPT=~/opt/miniconda3/etc/profile.d/conda.sh
    CONDA_BIN=~/opt/miniconda3/envs/ascent/bin
fi

source $CONDA_SETUP_SCRIPT

# package installation
conda create -n ascent -y
conda activate ascent
conda install -y python=3.7
python "$($CONDA_BIN)/pip" install --upgrade pip setuptools wheel
python "$($CONDA_BIN)/pip" install pillow>=5.2.0 numpy>=1.16.4 matplotlib>=3.2.1 pyclipper>=1.1.0 pygame>=1.9.6 pymunk>=5.5.0 scipy>=1.1.0 pandas>=0.25.1 openpyxl>=3.0.3 opencv-python quantiphy
conda install -y shapely
rm =*  # weird bug where pip creates empty files named "=<version>"

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

echo "alias ascent_setup='source $CONDA_SETUP_SCRIPT; conda activate ascent; cd $PWD'" >> ~/.bash_profile
echo "Added. Remember to run 'ascent_setup' to use (requires shell restart)."
exit 0