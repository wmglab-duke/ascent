$title    = 'First-Time Question'
$question = 'Is this your first time running this script?'
$choices  = '&Yes', '&No'

$decision = $Host.UI.PromptForChoice($title, $question, $choices, 1)
if ($decision -eq 0) {
    conda init powershell
    Write-Host 'ran "conda init powershell" to set up conda for powershell."`n"Please restart Anaconda Powershell Prompt and answer "no" to this question upon re-running the installation script.'
} else {
    Write-Host 'Great, assuming "conda init powershell" has already been run'

    conda create --name ascent -y
    conda activate ascent
    conda install -y -c conda-forge -c cogsci pip pillow numpy shapely matplotlib pyclipper pygame opencv libtiff=4.0 pymunk scipy pandas openpyxl
    pip install quantiphy
    
    $title    = 'Conda Default Environment'
    $question = 'Do you want to set "ascent" as your default Conda environment?'
    $choices  = '&Yes', '&No'
    
    $decision = $Host.UI.PromptForChoice($title, $question, $choices, 1)
    if ($decision -eq 0) {
        $filename = 'Microsoft.PowerShell_profile.ps1'
        $filepath = "C:\Users\$($env:UserName)\Documents\WindowsPowerShell\"
        $filecontent = "conda activate ascent"

        New-Item -Path "$filepath" -Name "$filename" -ItemType "file" -Value "$filecontent"
        
        Write-Host 'Set "ascent" as default Conda environment'
    } else {
        Write-Host 'Did not set "ascent" as default Conda environment'
    }
}


