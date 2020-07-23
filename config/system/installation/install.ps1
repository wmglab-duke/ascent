conda create -y ascent
conda activate ascent
conda install -y -c conda-forge pillow numpy shapely matplotlib pyclipper pygame quantiphy opencv libtiff=4.0 python=3.7 pymunk scipy pandas openpyxl shutil

$title    = 'Conda Default Environment'
$question = 'Do you want to set "ascent" as your default Conda environment?'
$choices  = '&Yes', '&No'

$decision = $Host.UI.PromptForChoice($title, $question, $choices, 1)
if ($decision -eq 0) {
    New-item –type file –force $profile
    Add-Content -Path "C:\Users\$($env:UserName)\Documents\WindowsPowerShell\" -Value "conda activate ascent"
    Write-Host 'Set "ascent" as default Conda environment'
} else {
    Write-Host 'Did not set "ascent" as default Conda environment'
}
