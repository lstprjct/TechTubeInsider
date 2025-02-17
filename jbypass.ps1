$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12

$scriptUrl = "https://raw.githubusercontent.com/lstprjct/TechTubeInsider/main/jbypass.py"

# Generate a unique temp file
$rand = Get-Random -Maximum 99999999
$scriptPath = "$env:TEMP\docomo_$rand.py"

try {
    # Download the script
    Invoke-RestMethod -Uri $scriptUrl -OutFile $scriptPath

    # Run the Python script and wait for it to finish
    Start-Process -FilePath "python" -ArgumentList "`"$scriptPath`"" -Wait -NoNewWindow
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)"
} finally {
    # Ensure cleanup happens even if an error occurs
    if (Test-Path $scriptPath) {
        Remove-Item -Path $scriptPath -Force
    }
}
