#! /bin/bash
set -e
conda init
CONDA_ENVPY=$(conda info --base)/envs/ascent/bin/python
CONDA_BASE=$(conda info --base)/etc/profile.d/conda.sh
source $CONDA_BASE
conda create -n ascent
eval "$(conda shell.bash hook)"
conda activate ascent
conda install python=3.11
$CONDA_ENVPY -m pip install --upgrade pip setuptools wheel
$CONDA_ENVPY -m pip install -r requirements.txt
conda install -c conda-forge ffmpeg

echo
# create shortcut
read -p "Add ASCENT environment setup alias to '.bash_profile'? (recommended) [y/N] " yn
case $yn in
    [Yy]* )
        echo "alias ascent_setup='source $CONDA_BASE; conda activate ascent; cd $PWD'" >> ~/.bash_profile
        echo "Added. Remember to run 'ascent_setup' to use (requires shell restart)."
        ;;
    [Nn]* ) echo "Not added";;
esac
exit 0
