# package installation
$ErrorActionPreference = "Stop"
conda init powershell
conda create -n ascent
conda activate ascent
conda install python=3.11
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
conda install -c conda-forge ffmpeg
