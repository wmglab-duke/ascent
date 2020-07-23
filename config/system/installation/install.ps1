conda init powershell
conda create --name ascent -y
conda activate ascent
conda install -y -c conda-forge -c cogsci pip pillow numpy shapely matplotlib pyclipper pygame opencv libtiff=4.0 pymunk scipy pandas openpyxl
pip install quantiphy

$title    = 'Conda Default Environment'
$question = 'Do you want to set "ascent" as your default Conda environment?'
$choices  = '&Yes', '&No'

$decision = $Host.UI.PromptForChoice($title, $question, $choices, 1)
if ($decision -eq 0) {
    New-item –type file –force "$profile"
    Add-Content -Path "C:\Users\$($env:UserName)\Documents\WindowsPowerShell\" -Value "conda activate ascent"
    Write-Host 'Set "ascent" as default Conda environment'
} else {
    Write-Host 'Did not set "ascent" as default Conda environment'
}
