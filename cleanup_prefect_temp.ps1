# PowerShell script to clean up Prefect temporary directories
# Run this if you encounter permission errors with strava_analytics-agent directories

Write-Host "🧹 Cleaning up Prefect temporary directories..." -ForegroundColor Yellow

# Stop any running Prefect processes
Write-Host "Stopping Prefect processes..." -ForegroundColor Blue
Get-Process | Where-Object {$_.ProcessName -like "*prefect*"} | Stop-Process -Force -ErrorAction SilentlyContinue

# Wait a moment for processes to fully stop
Start-Sleep -Seconds 2

# Remove temporary directories
$tempDirs = @("strava_analytics-agent", "*-agent")
foreach ($dir in $tempDirs) {
    if (Test-Path $dir) {
        Write-Host "Removing directory: $dir" -ForegroundColor Green
        try {
            Remove-Item -Recurse -Force $dir -ErrorAction Stop
            Write-Host "✅ Successfully removed $dir" -ForegroundColor Green
        }
        catch {
            Write-Host "❌ Failed to remove $dir : $($_.Exception.Message)" -ForegroundColor Red
            Write-Host "💡 Try running this script as Administrator" -ForegroundColor Yellow
        }
    }
}

# Check Git status
Write-Host "Checking Git status..." -ForegroundColor Blue
git status

Write-Host "🎉 Cleanup completed!" -ForegroundColor Green
Write-Host "💡 If you still have issues, try:" -ForegroundColor Yellow
Write-Host "   1. Run this script as Administrator" -ForegroundColor White
Write-Host "   2. Restart your terminal/IDE" -ForegroundColor White
Write-Host "   3. Check for any locked files with Process Explorer" -ForegroundColor White
