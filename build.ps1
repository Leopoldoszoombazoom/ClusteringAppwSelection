# Builds ClusteringApp.exe with PyInstaller (Python not needed on the target PC).
# Usage (from the repo folder):   powershell -ExecutionPolicy Bypass -File build.ps1
# Output:  dist\ClusteringApp\ClusteringApp.exe   and   dist\ClusteringApp-windows.zip

$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$app = 'ClusterigAppwSelection'

# 1. Virtual environment with the app's libraries + PyInstaller
if (-not (Test-Path .venv)) { python -m venv .venv }
.\.venv\Scripts\python.exe -m pip install --quiet -r requirements.txt pyinstaller

# 2. Bundle the icon and every dataset next to the program
$data = @('python.ico', 'winequality-red.csv', 'winequality-white.csv', 'HTRU_2.csv',
          'ecoli.data', 'yeast.data', 'abalone.data', 'iris.data',
          'Data_Cortex_Nuclear.xls', 'BreastTissue.xls', 'CTG 2.xls')
$addData = foreach ($f in $data) { '--add-data'; "$app\$f;." }

# 3. Build (--windowed = no black console window behind the app)
.\.venv\Scripts\pyinstaller.exe --noconfirm --clean --windowed `
    --name ClusteringApp --icon "$app\python.ico" `
    @addData "$app\LoadMyProjectwith3Selections.py"

# 4. Zip it for sharing (e.g. as a GitHub Release asset)
Compress-Archive -Path dist\ClusteringApp -DestinationPath dist\ClusteringApp-windows.zip -Force
Write-Host "Done: dist\ClusteringApp\ClusteringApp.exe"
