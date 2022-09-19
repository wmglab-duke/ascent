# package installation
$ErrorActionPreference = "Stop"
conda init powershell
conda create -n ascent python=3.7 pip setuptools wheel shapely
conda activate ascent
pip install -r requirements.txt
conda install -c conda-forge ffmpeg
