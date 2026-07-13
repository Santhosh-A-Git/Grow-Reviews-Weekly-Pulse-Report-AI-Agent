Start-Process powershell -ArgumentList "-NoExit -Command py -m uvicorn src.api:app --port 8000"
Start-Process powershell -ArgumentList "-NoExit -Command `$env:Path = 'C:\Program Files\nodejs;' + `$env:Path; cd frontend; & 'C:\Program Files\nodejs\npm.cmd' run dev"
