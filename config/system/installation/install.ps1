# package installation
conda create -n ascent python=3.7
conda activate ascent
pip install -r requirements.txt

# shortcut creation
$title    = 'ASCENT Conda Environment'
$question = 'Do you want to save a shortcut for the "ascent" Conda environment to your Desktop?'
$choices  = '&Yes', '&No'
$decision = $Host.UI.PromptForChoice($title, $question, $choices, 1)
if ($decision -eq 0) {
    $Arguments = "-ExecutionPolicy ByPass -NoExit -Command `"& `'C:\Users\" + $env:UserName + "\Miniconda3\shell\condabin\conda-hook.ps1`' ; conda activate ascent; cd `'" + (Get-Item .).FullName + "`'"
    $TargetFile = '%windir%\System32\WindowsPowerShell\v1.0\powershell.exe'
    $ShortcutFile = 'ASCENT.lnk'
    $WScriptShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WScriptShell.CreateShortcut($ShortcutFile)
    $Shortcut.TargetPath = $TargetFile
    $Shortcut.Arguments = $Arguments
    $Shortcut.Save()

    Write-Host 'Saved shortcut to ' $ShortcutFile

} else {
    Write-Host 'Did not save shortcut.'
}
