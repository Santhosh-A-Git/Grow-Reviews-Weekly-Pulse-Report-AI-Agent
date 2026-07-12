$Action = New-ScheduledTaskAction -Execute "py" -Argument "src\main.py" -WorkingDirectory "d:\S\S\PM -NEXT LEAP\Projects\AI Agent"
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 9:00AM
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable
$TaskName = "Groww AI Agent Weekly Pulse"

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Runs the Groww AI Agent Pipeline every Monday morning"

Write-Host "Scheduled task '$TaskName' has been created successfully!"
Write-Host "It will run automatically every Monday at 9:00 AM."
