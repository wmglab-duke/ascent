#! /bin/bash

# set up conda for this environment, choosing between Linux/macOS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    CONDA_SETUP_SCRIPT=/hpc/group/wmglab/jec91/miniconda3/etc/profile.d/conda.bash
    CONDA_BIN=/hpc/group/wmglab/jec91/miniconda3/envs/ascent/bin
else
    # macOS
    CONDA_SETUP_SCRIPT=~/opt/miniconda3/etc/profile.d/conda.sh
    CONDA_BIN=~/opt/miniconda3/envs/ascent/bin
fi

conda init
CONDA_ENVPY=$(conda info --base)/envs/ascent/bin/python
CONDA_BASE=$(conda info --base)/etc/profile.d/conda.sh
source $CONDA_BASE
conda create -n ascent python=3.7 pip setuptools wheel shapely
eval "$(conda shell.bash hook)"
conda activate ascent
$CONDA_ENVPY -m pip install -r requirements.txt

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
