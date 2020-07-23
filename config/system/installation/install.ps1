# ensure current directory is root of pipeline
$title    = 'Current Directory'
$question = 'Have you navigated to the root of the ASCENT repository?'
$choices  = '&Yes', '&No'
$decision = $Host.UI.PromptForChoice($title, $question, $choices, 1)
if ($decision -eq 0) {
    Write-Host 'Great, proceeding with installation.'

    # package installation
    conda create --name ascent -y
    conda activate ascent
    conda install -y -c conda-forge -c cogsci pip pillow numpy shapely matplotlib pyclipper pygame opencv libtiff=4.0 pymunk scipy pandas openpyxl
    pip install quantiphy
    
    # shortcut creation
    $title    = 'ASCENT Conda Environment'
    $question = 'Do you want to save a shortcut for the "ascent" Conda environment to your Desktop?'
    $choices  = '&Yes', '&No'
    $decision = $Host.UI.PromptForChoice($title, $question, $choices, 1)
    if ($decision -eq 0) {
        $EnvCommand = "`"& `'C:\Users\" + $env:UserName + "\Miniconda3\shell\condabin\conda-hook.ps1`' ; conda activate `'C:\Users\jec91\Miniconda3\ascent`'" + "; cd `'" + (Get-Item .).FullName + "`'"
        $TargetFile = "%windir%\System32\WindowsPowerShell\v1.0\powershell.exe -ExecutionPolicy ByPass -NoExit -Command " + $EnvCommand
        $ShortcutFile = 'Desktop\ASCENT Powershell Prompt.lnk'
        $WScriptShell = New-Object -ComObject "Shell.Application"
        $Shortcut = $WScriptShell.CreateShortcut($ShortcutFile)
        Write-Host $TargetFile
        $Shortcut.TargetPath = $TargetFile
        $Shortcut.Save()
        
        Write-Host 'Saved shortcut to Desktop'

    } else {
        Write-Host 'Did not save shortcut to Desktop'
    }
} else {
    Write-Host 'Please do so and re-run.'
}


