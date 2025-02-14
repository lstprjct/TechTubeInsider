Invoke-Command -ComputerName RemotePC -ScriptBlock {
    $scriptUrl = "https://raw.githubusercontent.com/lstprjct/TechTubeInsider/main/docomo.py"
    $scriptPath = "$env:TEMP\docomo.py"
    Invoke-RestMethod -Uri $scriptUrl -OutFile $scriptPath
    & python $scriptPath
}
