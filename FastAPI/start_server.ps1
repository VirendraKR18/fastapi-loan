# Start FastAPI Server with Virtual Environment
$ErrorActionPreference = "Stop"

# Change to script directory
Set-Location $PSScriptRoot

# Activate virtual environment and start server
& ".\.venv\Scripts\python.exe" run_dev.py
