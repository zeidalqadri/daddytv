<#
.SYNOPSIS
Sets up get_iplayer for automated downloads on Windows.

.DESCRIPTION
This script performs the following actions:
- Checks for and prompts the user to install necessary dependencies (Git, Strawberry Perl, ffmpeg).
- Clones or updates the get_iplayer source code from GitHub.
- Installs required Perl modules using cpanm.
- Prompts the user for the Google Drive download path.
- Configures get_iplayer preferences (output path, ffmpeg path).
- Prompts the user for shows to add to the PVR list.
- Creates a helper script (run_downloads.ps1) to trigger PVR downloads.
- Creates a Windows Scheduled Task to run downloads automatically.
- Optionally creates Desktop shortcuts.

.NOTES
Requires PowerShell 5.1 or later.
Must be run with Administrator privileges for some operations (PATH update, Scheduled Task).
User interaction is required for dependency installation and configuration inputs.
Assumes Google Drive for Desktop is already installed and configured by the user.
#>

# --- Configuration ---
$InstallBaseDir = "C:\Tools" # Base directory for tools
$GetIplayerDir = Join-Path $InstallBaseDir "get_iplayer_dev"
$FfmpegDir = Join-Path $InstallBaseDir "ffmpeg"
$FfmpegBinDir = Join-Path $FfmpegDir "bin"
$FfmpegExePath = Join-Path $FfmpegBinDir "ffmpeg.exe"
$RunDownloadsScriptPath = Join-Path $InstallBaseDir "run_downloads.ps1"
$ScheduledTaskName = "GetIplayerDailyDownload"
$PerlModules = @(
    "LWP::Protocol::https"
    "Mojolicious"
    "Mozilla::CA"
    "XML::LibXML"
    "IO::Socket::SSL"
    "Digest::SHA"
    # Add any other modules identified as required by get_iplayer
)
# URL for a reliable static ffmpeg build (check gyan.dev or BtbN for latest)
$FfmpegDownloadUrl = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"

# --- Helper Functions ---
function Test-CommandExists {
    param($Command)
    return [bool](Get-Command $Command -ErrorAction SilentlyContinue)
}

function Add-ToPath {
    param(
        [string]$Directory,
        [string]$Scope = "User" # Can be "User" or "Machine"
    )
    try {
        $CurrentPath = [Environment]::GetEnvironmentVariable("Path", $Scope)
        if (-not ($CurrentPath -split ';' -contains $Directory)) {
            Write-Host "Adding '$Directory' to $Scope PATH..."
            $NewPath = "$CurrentPath;$Directory"
            [Environment]::SetEnvironmentVariable("Path", $NewPath, $Scope)
            # Update current session's PATH
            $env:Path = $NewPath
            Write-Host "'$Directory' added to $Scope PATH. Please restart PowerShell for changes to take full effect in new sessions." -ForegroundColor Green
        } else {
            Write-Host "'$Directory' already exists in $Scope PATH." -ForegroundColor Cyan
        }
    } catch {
        Write-Error "Failed to add '$Directory' to $Scope PATH: $_"
    }
}

# --- Script Start ---

# 1. Check for Administrator Privileges
Write-Host "Checking for Administrator privileges..."
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Warning "This script needs Administrator privileges to modify PATH and create Scheduled Tasks."
    Write-Warning "Please re-run this script as an Administrator (Right-click -> Run as administrator)."
    Read-Host "Press Enter to exit..."
    exit 1
}
Write-Host "Running with Administrator privileges." -ForegroundColor Green

# 2. Welcome
Write-Host "-------------------------------------" -ForegroundColor Yellow
Write-Host " get_iplayer Automated Setup for Windows " -ForegroundColor Yellow
Write-Host "-------------------------------------" -ForegroundColor Yellow
Write-Host "This script will guide you through setting up get_iplayer."
Write-Host "It will check for dependencies, download necessary files, configure settings,"
Write-Host "and set up automated downloads to your Google Drive folder."
Write-Host "User interaction will be required."
Read-Host "Press Enter to continue..."

# 3. Create Base Directory
if (-not (Test-Path $InstallBaseDir)) {
    Write-Host "Creating base installation directory: $InstallBaseDir"
    try {
        New-Item -ItemType Directory -Path $InstallBaseDir -ErrorAction Stop | Out-Null
    } catch {
        Write-Error "Failed to create base directory '$InstallBaseDir'. Please check permissions. Error: $_"
        Read-Host "Press Enter to exit..."
        exit 1
    }
}

# 4. Check for Git (Manual Install Required)
Write-Host "`n--- Checking for Git ---"
if (-not (Test-CommandExists "git")) {
    Write-Error "Git is not found in your PATH."
    Write-Host "Git is required to download the latest get_iplayer code."
    Write-Host "Please download and install Git for Windows from: https://git-scm.com/download/win"
    Write-Host "During installation, ensure you select an option that adds Git to the PATH (usually the default)."
    Write-Error "Re-run this script after Git has been successfully installed."
    Read-Host "Press Enter to exit..."
    exit 1
}
Write-Host "Git found." -ForegroundColor Green

# 5. Check for Strawberry Perl (Manual Install Required)
Write-Host "`n--- Checking for Strawberry Perl ---"
$PerlPath = Get-Command perl -ErrorAction SilentlyContinue
$IsStrawberryPerl = $false
if ($PerlPath) {
    # Basic check if it looks like Strawberry Perl
    if ($PerlPath.Source -like "*Strawberry*") {
        $IsStrawberryPerl = $true
        Write-Host "Found Perl at: $($PerlPath.Source)"
    } else {
        Write-Warning "Found a Perl installation, but it might not be Strawberry Perl: $($PerlPath.Source)"
        Write-Warning "Strawberry Perl is recommended for compatibility."
        $confirmNonStrawberry = Read-Host "Do you want to continue with this Perl installation? (y/n)"
        if ($confirmNonStrawberry -ne 'y') {
            $PerlPath = $null # Force prompt to install Strawberry
        } else {
             $IsStrawberryPerl = $true # User wants to proceed anyway
        }
    }
}

if (-not $IsStrawberryPerl) {
    Write-Error "Strawberry Perl is not found or not accessible in PATH."
    Write-Host "Strawberry Perl is required to run get_iplayer and install modules."
    Write-Host "Please download and install the latest 64-bit version from: https://strawberryperl.com/"
    Write-Host "Ensure it's added to the system PATH during installation."
    Write-Error "Re-run this script after Strawberry Perl has been successfully installed."
    Read-Host "Press Enter to exit..."
    exit 1
}
Write-Host "Strawberry Perl found." -ForegroundColor Green
$PerlExePath = $PerlPath.Source

# 6. Check/Download ffmpeg
Write-Host "`n--- Checking for ffmpeg ---"
if (-not (Test-Path $FfmpegExePath) -and -not (Test-CommandExists "ffmpeg")) {
    Write-Warning "ffmpeg not found."
    Write-Host "Downloading ffmpeg essentials build from gyan.dev..."
    $FfmpegZipPath = Join-Path $env:TEMP "ffmpeg-release-essentials.zip"
    try {
        Invoke-WebRequest -Uri $FfmpegDownloadUrl -OutFile $FfmpegZipPath -ErrorAction Stop
        Write-Host "Download complete. Extracting..."
        if (-not (Test-Path $FfmpegDir)) { New-Item -ItemType Directory -Path $FfmpegDir -Force | Out-Null }
        Expand-Archive -Path $FfmpegZipPath -DestinationPath $FfmpegDir -Force -ErrorAction Stop
        # The zip extracts to a folder like "ffmpeg-7.0-essentials_build", find it
        $ExtractedFolder = Get-ChildItem -Path $FfmpegDir -Directory | Select-Object -First 1
        if ($ExtractedFolder) {
            # Move contents of bin up to our target bin
            $SourceBin = Join-Path $ExtractedFolder.FullName "bin"
            if (Test-Path $SourceBin) {
                 if (-not (Test-Path $FfmpegBinDir)) { New-Item -ItemType Directory -Path $FfmpegBinDir -Force | Out-Null }
                 Move-Item -Path (Join-Path $SourceBin "*") -Destination $FfmpegBinDir -Force
                 # Clean up empty extracted folder structure
                 Remove-Item -Path $ExtractedFolder.FullName -Recurse -Force
            } else {
                 Write-Warning "Could not find 'bin' directory in extracted ffmpeg archive."
            }
        } else {
             Write-Warning "Could not find extracted ffmpeg folder."
        }
        Remove-Item $FfmpegZipPath -Force
        Write-Host "ffmpeg extracted to $FfmpegBinDir" -ForegroundColor Green
    } catch {
        Write-Error "Failed to download or extract ffmpeg. Error: $_"
        Write-Host "Please manually download ffmpeg from https://www.gyan.dev/ffmpeg/builds/ (essentials build recommended)"
        Write-Host "Extract the contents, and place ffmpeg.exe and ffprobe.exe into $FfmpegBinDir"
        Read-Host "Press Enter after manually placing ffmpeg files..."
        if (-not (Test-Path $FfmpegExePath)) {
             Write-Error "ffmpeg.exe still not found in $FfmpegBinDir. Exiting."
             Read-Host "Press Enter to exit..."
             exit 1
        }
    }
    # Add ffmpeg bin to User PATH persistently
    Add-ToPath -Directory $FfmpegBinDir -Scope User
} else {
     # If ffmpeg command exists but not in our expected path, find it
     if (-not (Test-Path $FfmpegExePath) -and (Test-CommandExists "ffmpeg")) {
         $FfmpegExePath = (Get-Command ffmpeg).Source
         Write-Host "Found existing ffmpeg in PATH: $FfmpegExePath" -ForegroundColor Cyan
     } else {
         Write-Host "Found ffmpeg at: $FfmpegExePath" -ForegroundColor Green
     }
}

# 7. Clone/Update get_iplayer Source Code
Write-Host "`n--- Getting get_iplayer Source Code ---"
if (-not (Test-Path $GetIplayerDir)) {
    Write-Host "Cloning get_iplayer repository into $GetIplayerDir..."
    try {
        # Run git clone and capture output/errors
        $cloneResult = git clone https://github.com/get-iplayer/get_iplayer.git $GetIplayerDir 2>&1
        # Check exit code AND if the directory was actually created
        if ($LASTEXITCODE -ne 0 -or -not (Test-Path $GetIplayerDir -PathType Container)) {
            Write-Error "Failed to clone get_iplayer repository. Please check network connection and permissions for C:\Tools."
            Write-Error "Git output (if any): $cloneResult"
            # Throw an exception to be caught by the outer catch block is cleaner, but for simplicity let's exit here
            Read-Host "Press Enter to exit..."
            exit 1
        }
        Write-Host "Repository cloned successfully." -ForegroundColor Green
    } catch {
        # This catch might not be reached if git clone fails but doesn't throw terminating error
        Write-Error "An unexpected error occurred during git clone: $_"
        Read-Host "Press Enter to exit..."
        exit 1
    }
} else {
    Write-Host "Updating existing get_iplayer repository in $GetIplayerDir..."
    try {
        Push-Location $GetIplayerDir
        # Run git pull and capture output/errors
        $pullResult = git pull 2>&1
        if ($LASTEXITCODE -ne 0) {
             Write-Warning "git pull command failed. Git output (if any): $pullResult"
             # Don't necessarily exit, but warn the user we might be using old code
             Write-Warning "Continuing with potentially outdated local code."
        } else {
             Write-Host "Repository updated successfully." -ForegroundColor Green
        }
        Pop-Location
    } catch {
        Pop-Location # Ensure we pop location even if git pull fails catastrophically
        Write-Error "Failed to update get_iplayer repository. Error: $_"
        Write-Warning "Continuing with potentially outdated local code."
    }
}
# Verify the script file exists AFTER clone/update attempt
$GetIplayerScript = Join-Path $GetIplayerDir "get_iplayer"
# Check it's specifically a file (Leaf)
if (-not (Test-Path $GetIplayerScript -PathType Leaf)) {
     Write-Error "Failed to find the main get_iplayer script file at '$GetIplayerScript' after clone/update."
     Write-Error "The clone or update might have failed silently, or the repository structure may have changed."
     Write-Error "Please check the contents of '$GetIplayerDir' manually."
     Read-Host "Press Enter to exit..."
     exit 1
}

# 8. Install/Update Perl Modules
Write-Host "`n--- Installing/Updating Perl Modules ---"
Write-Host "This may take several minutes..."
$LogFile = Join-Path $InstallBaseDir "perl_module_install.log"
Write-Host "Installation progress and errors will be logged to: $LogFile"
# Ensure cpanm is installed
Write-Host "Checking/Installing cpanm..."
$CpanmInstalled = $false
try {
    # Run cpan command to install cpanm, redirect output to log
    & $PerlExePath -MCPAN -e "CPAN::Shell->install('App::cpanminus')" *>> $LogFile
    # Find cpanm executable (might be in Strawberry Perl's bin or site/bin)
    $CpanmPath = Get-Command cpanm -ErrorAction SilentlyContinue
    if (-not $CpanmPath) {
        # Try common Strawberry Perl paths
        $PossibleCpanmPaths = @(
             Join-Path (Split-Path $PerlExePath -Parent) "cpanm.bat" # e.g., C:\Strawberry\perl\bin\cpanm.bat
             Join-Path (Split-Path $PerlExePath -Parent | Split-Path -Parent) "c\bin\cpanm.bat" # Sometimes in C:\Strawberry\c\bin
             Join-Path (Split-Path $PerlExePath -Parent | Split-Path -Parent) "perl\site\bin\cpanm"
             Join-Path (Split-Path $PerlExePath -Parent | Split-Path -Parent) "perl\site\bin\cpanm.bat"
        )
        $CpanmPath = $PossibleCpanmPaths | Where-Object { Test-Path $_ } | Select-Object -First 1

        if (-not $CpanmPath) {
             Write-Error "Could not find cpanm executable after installation attempt. Check $LogFile for details."
             Read-Host "Press Enter to exit..."
             exit 1
        }
         Write-Host "Found cpanm at $CpanmPath"
         $CpanmInstalled = $true
    } else {
         $CpanmPath = $CpanmPath.Source
         $CpanmInstalled = $true
    }
} catch {
     Write-Error "Failed to install cpanm. Check $LogFile for details. Error: $_"
     Read-Host "Press Enter to exit..."
     exit 1
}

if ($CpanmInstalled) {
    Write-Host "Installing required modules using cpanm (logging to $LogFile)..."
    $AllModulesOk = $true
    foreach ($module in $PerlModules) {
        Write-Host "Attempting to install $module..."
        try {
            # Use Start-Process to better capture streams and check exit code
            $process = Start-Process -FilePath $CpanmPath -ArgumentList "--verbose", $module -Wait -PassThru -RedirectStandardOutput $LogFile -Append -RedirectStandardError $LogFile -Append
            if ($process.ExitCode -ne 0) {
                Write-Error "Failed to install module '$module'. Exit code: $($process.ExitCode)."
                $AllModulesOk = $false
            } else {
                 Write-Host "'$module' installation successful or already up-to-date." -ForegroundColor Green
            }
        } catch {
             Write-Error "Error occurred running cpanm for '$module': $_"
             $AllModulesOk = $false
        }
    }

    if (-not $AllModulesOk) {
        Write-Error "One or more required Perl modules failed to install."
        Write-Error "Please check the log file for details: $LogFile"
        Write-Error "You may need to resolve dependencies or install build tools (like dmake via 'gmake' in Strawberry Perl) manually."
        Read-Host "Press Enter to exit..."
        exit 1
    } else {
        Write-Host "All required Perl modules installed successfully." -ForegroundColor Green
    }
}

# 9. Get & Verify Google Drive Path
Write-Host "`n--- Configure Download Destination ---"
$GDrivePath = ""
while (-not (Test-Path $GDrivePath -PathType Container)) {
    $GDrivePath = Read-Host "IMPORTANT: Please enter the FULL path to the folder where downloads should be saved (e.g., C:\Users\YourUser\Google Drive\iPlayerDownloads)"
    if (-not (Test-Path $GDrivePath -PathType Container)) {
        Write-Warning "Path '$GDrivePath' does not exist or is not a folder. Please try again."
    } else {
         Write-Host "Using download path: $GDrivePath" -ForegroundColor Green
     }
}

# 10. Configure get_iplayer Preferences
Write-Host "`n--- Configuring get_iplayer ---"
try {
    Write-Host "Setting default output directory..."
    & $PerlExePath $GetIplayerScript --prefs-add --output="$GDrivePath"
    Write-Host "Setting ffmpeg path..."
    & $PerlExePath $GetIplayerScript --prefs-add --ffmpeg="$FfmpegExePath"
    # Add other useful defaults? e.g., subtitles
    # & $PerlExePath $GetIplayerScript --prefs-add --subtitles=1
    Write-Host "Preferences saved." -ForegroundColor Green
} catch {
     Write-Error "Failed to set get_iplayer preferences: $_"
}

# 11. Configure PVR List (Shows to Download)
Write-Host "`n--- Configure Shows for Automatic Download (PVR List) ---"
$AddMoreShows = 'y'
while ($AddMoreShows -eq 'y') {
    $ShowName = Read-Host "Enter the exact name of a TV show to automatically download (or press Enter to skip/finish)"
    if ([string]::IsNullOrWhiteSpace($ShowName)) {
        $AddMoreShows = 'n'
    } else {
        Write-Host "Adding '$ShowName' to PVR list..."
        try {
             & $PerlExePath $GetIplayerScript --pvr-add "$ShowName"
        } catch {
             Write-Error "Failed to add '$ShowName' to PVR list: $_"
        }
        $AddMoreShows = Read-Host "Add another show? (y/n)"
     }
}

# 12. Create the run_downloads.ps1 Script
Write-Host "`n--- Creating Helper Script for Downloads ---"
$RunScriptContent = @"
# This script runs the get_iplayer PVR download process.
# It should be run by the Windows Task Scheduler.

Write-Host "Starting get_iplayer PVR download check..."
try {
    # Ensure we use the correct Perl and script path
    & "$PerlExePath" "$GetIplayerScript" --pvr
    Write-Host "PVR download check finished."
} catch {
    Write-Error "Error running get_iplayer PVR: `$_"
    # Consider adding more robust logging here
}
# Optional: Pause briefly if run manually to see output
# Start-Sleep -Seconds 10
"@
try {
    Set-Content -Path $RunDownloadsScriptPath -Value $RunScriptContent -Encoding UTF8 -Force
    Write-Host "Helper script created at $RunDownloadsScriptPath" -ForegroundColor Green
} catch {
     Write-Error "Failed to create helper script '$RunDownloadsScriptPath': $_"
}


# 13. Create Scheduled Task
Write-Host "`n--- Creating Scheduled Task for Automatic Downloads ---"
$TaskAction = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$RunDownloadsScriptPath`""
# Run daily at 3:00 AM
$TaskTrigger = New-ScheduledTaskTrigger -Daily -At 3am
$TaskPrincipal = New-ScheduledTaskPrincipal -UserId "NT AUTHORITY\SYSTEM" -LogonType ServiceAccount -RunLevel Highest # Run even if user logged off
$TaskSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -WakeToRun -ExecutionTimeLimit (New-TimeSpan -Days 1) -MultipleInstances IgnoreNew

try {
    # Unregister task first if it exists, to allow updates
    Get-ScheduledTask -TaskName $ScheduledTaskName -ErrorAction SilentlyContinue | Unregister-ScheduledTask -Confirm:$false
    Register-ScheduledTask -TaskName $ScheduledTaskName -Action $TaskAction -Trigger $TaskTrigger -Principal $TaskPrincipal -Settings $TaskSettings -Description "Automatically downloads new episodes of selected shows using get_iplayer." -Force
    Write-Host "Scheduled Task '$ScheduledTaskName' created successfully." -ForegroundColor Green
    Write-Host "It will run daily at 3:00 AM."
} catch {
    Write-Error "Failed to create Scheduled Task '$ScheduledTaskName'. Error: $_"
     Write-Warning "Automatic downloads will not run. You can run downloads manually using the helper script."
}

# 14. Create Desktop Shortcuts (Optional)
Write-Host "`n--- Creating Desktop Shortcuts (Optional) ---"
$CreateShortcuts = Read-Host "Create shortcuts on the Desktop to run setup again and trigger downloads manually? (y/n)"
if ($CreateShortcuts -eq 'y') {
    try {
        $Shell = New-Object -ComObject WScript.Shell
        $DesktopPath = [Environment]::GetFolderPath("Desktop")

        # Shortcut to run downloads manually
        $ManualRunShortcutPath = Join-Path $DesktopPath "Run iPlayer Downloads Now.lnk"
        $Shortcut = $Shell.CreateShortcut($ManualRunShortcutPath)
        $Shortcut.TargetPath = "powershell.exe"
        $Shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$RunDownloadsScriptPath`""
        $Shortcut.WorkingDirectory = $InstallBaseDir
        $Shortcut.IconLocation = "imageres.dll,110" # Download icon
        $Shortcut.Description = "Manually check for and download new episodes using get_iplayer."
        $Shortcut.Save()
        Write-Host "Created 'Run iPlayer Downloads Now' shortcut on Desktop." -ForegroundColor Green

        # Shortcut to run setup again (useful for adding shows later)
        $SetupShortcutPath = Join-Path $DesktopPath "Configure iPlayer Downloads.lnk"
        $Shortcut = $Shell.CreateShortcut($SetupShortcutPath)
        $Shortcut.TargetPath = "powershell.exe"
        $Shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" # $PSCommandPath is path to this script
        $Shortcut.WorkingDirectory = Split-Path $PSCommandPath -Parent
        $Shortcut.IconLocation = "imageres.dll,109" # Settings icon
        $Shortcut.Description = "Run the setup script again to add/remove shows or reconfigure settings."
        $Shortcut.Save()
         Write-Host "Created 'Configure iPlayer Downloads' shortcut on Desktop." -ForegroundColor Green

    } catch {
        Write-Error "Failed to create Desktop shortcuts: $_"
     }
}

# --- Function to Get Primary IPv4 Address --- (Keep this function definition)
function Get-PrimaryIPv4Address {
    try {
        # Get network adapters that are up and not loopback or virtual
        $adapters = Get-NetAdapter -Physical | Where-Object {$_.Status -eq 'Up' -and $_.InterfaceDescription -notlike '*Loopback*' -and $_.InterfaceDescription -notlike '*Virtual*'}
        if (-not $adapters) {
            Write-Warning "Could not find an active physical network adapter."
            return $null
        }
        # Prioritize Ethernet, then Wi-Fi
        $primaryAdapter = $adapters | Sort-Object -Property {$_.MediaType -eq 'Ethernet'} -Descending | Select-Object -First 1

        $ipConfig = Get-NetIPConfiguration -InterfaceIndex $primaryAdapter.InterfaceIndex -ErrorAction SilentlyContinue
        $ipv4 = $ipConfig | Where-Object {$_.IPv4Address -ne $null} | Select-Object -ExpandProperty IPv4Address -First 1
        if ($ipv4) {
            return $ipv4.IPAddress
        } else {
            Write-Warning "Could not determine IPv4 address for adapter: $($primaryAdapter.Name)"
            return $null
        }
    } catch {
        Write-Warning "Error getting IP address: $_"
        return $null
    }
}

# 15. Final Instructions
Write-Host "`n--- Finding Current Local IP Address ---"
$CurrentIP = Get-PrimaryIPv4Address
if ($CurrentIP) {
    Write-Host "This computer's current local IP address appears to be: $CurrentIP" -ForegroundColor Cyan
    Write-Host "(Needed if connecting from TV via Network Share/SMB instead of Google Drive app)" -ForegroundColor Cyan
    Write-Warning "Note: This IP address might change later (DHCP). If TV connection fails, check the IP again in Windows Settings > Network."
} else {
    Write-Warning "Could not automatically determine the current local IP address."
    Write-Warning "If needed for network sharing, find it manually in Windows Settings > Network & Internet > Wi-Fi/Ethernet > Properties."
}


Write-Host "`n--- Setup Complete! ---" -ForegroundColor Green
Write-Host "Summary:"
Write-Host "- Dependencies checked (Perl, Git) - Manual installation required if missing."
Write-Host "- ffmpeg checked/downloaded."
Write-Host "- get_iplayer source code is in: $GetIplayerDir"
Write-Host "- Downloads will be saved to: $GDrivePath"
Write-Host "- Automatic downloads scheduled daily at 3:00 AM via Task Scheduler ($ScheduledTaskName)."
if ($CreateShortcuts -eq 'y') {
    Write-Host "- Shortcuts created on your Desktop."
}
Write-Host "`nIMPORTANT:"
Write-Host "- Ensure Google Drive for Desktop is running and signed in for downloads to sync."
Write-Host "- To watch downloads on TV, you have two main options:"
Write-Host "  1. Google Drive App on TV: Install and use the Google Drive app on your TV to browse and play files directly from the cloud."
Write-Host "  2. Network Share (SMB): Manually share the '$GDrivePath' folder on this computer using Windows File Explorer's sharing options. Then, use an app like VLC or Kodi on your TV to connect to the share using this computer's IP address (currently detected as $CurrentIP - but it might change!)."
Write-Host "- To add/remove shows later, run the 'Configure iPlayer Downloads' shortcut (if created) or re-run this setup script."

Read-Host "Press Enter to exit..."
