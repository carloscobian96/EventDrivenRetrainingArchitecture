# Simple manage.ps1 for Django using your venv
$venv_py = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$manage_py = Join-Path $PSScriptRoot "manage.py"
& $venv_py $manage_py @Args
