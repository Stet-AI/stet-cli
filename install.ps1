#Requires -Version 5.1
<#
.SYNOPSIS
  Install the latest stable Stet binary release on Windows (amd64).

.DESCRIPTION
  Windows counterpart to install.sh. Downloads the stet_Windows_x86_64.zip asset
  and checksums.txt from a release, verifies the SHA-256, validates that the zip
  contains exactly one member named stet.exe, and atomically installs it into the
  target directory.

  Use -Version to pin or roll back to an exact release tag.
#>
[CmdletBinding()]
param(
    [string]$Version = "",
    [string]$Repo,
    [string]$BinDir,
    [string]$DownloadBase,
    [switch]$Prerelease
)

$ErrorActionPreference = "Stop"

# PowerShell variable names are case-insensitive, so the working variables below
# use distinct names ($resolved*) and never alias the bound parameters ($Repo,
# $BinDir, $DownloadBase); reusing the parameter names (differing only in case)
# would silently clobber the caller-supplied values.

$AssetName = "stet_Windows_x86_64.zip"

function Die {
    param([string]$Message)
    [Console]::Error.WriteLine("stet install: $Message")
    exit 1
}

# --- Resolve --repo, mirroring install.sh's DEFAULT_REPO / repo_overridden logic ---
# STET_DIST_REPO overrides the hardcoded default but does NOT count as an explicit
# override; only an explicit -Repo argument flips to the gh-authenticated path.
$resolvedRepo = "Stet-AI/stet-cli"
if (-not [string]::IsNullOrEmpty($env:STET_DIST_REPO)) {
    $resolvedRepo = $env:STET_DIST_REPO
}
$repoOverridden = $false
if ($PSBoundParameters.ContainsKey('Repo') -and -not [string]::IsNullOrEmpty($Repo)) {
    $resolvedRepo = $Repo
    $repoOverridden = $true
}

# --- Resolve bin dir: -BinDir > $env:STET_INSTALL_DIR > $LOCALAPPDATA\Programs\stet ---
# The LOCALAPPDATA default is computed lazily so an explicit -BinDir/$STET_INSTALL_DIR
# works even when LOCALAPPDATA is unset (e.g. non-Windows test hosts).
$resolvedBinDir = $null
if (-not [string]::IsNullOrEmpty($env:STET_INSTALL_DIR)) {
    $resolvedBinDir = $env:STET_INSTALL_DIR
}
if ($PSBoundParameters.ContainsKey('BinDir') -and -not [string]::IsNullOrEmpty($BinDir)) {
    $resolvedBinDir = $BinDir
}
if ([string]::IsNullOrEmpty($resolvedBinDir)) {
    if ([string]::IsNullOrEmpty($env:LOCALAPPDATA)) {
        Die "cannot determine install dir: LOCALAPPDATA is unset; pass -BinDir"
    }
    $resolvedBinDir = Join-Path $env:LOCALAPPDATA "Programs\stet"
}

# --- Resolve download base: -DownloadBase > $env:STET_INSTALL_DOWNLOAD_BASE > https://github.com ---
$resolvedBase = "https://github.com"
if (-not [string]::IsNullOrEmpty($env:STET_INSTALL_DOWNLOAD_BASE)) {
    $resolvedBase = $env:STET_INSTALL_DOWNLOAD_BASE
}
if ($PSBoundParameters.ContainsKey('DownloadBase') -and -not [string]::IsNullOrEmpty($DownloadBase)) {
    $resolvedBase = $DownloadBase
}
$resolvedBase = $resolvedBase.TrimEnd('/')

# Public GitHub download when using the default repo and no explicit -Repo override;
# otherwise fall back to gh-authenticated access (private/overridden repo).
$usePublicDownload = ($resolvedRepo -eq "Stet-AI/stet-cli") -and (-not $repoOverridden)

if (-not $usePublicDownload) {
    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        Die "gh is required for -Repo/private installs; run: gh auth login"
    }
}

# Windows PowerShell 5.1 does not always negotiate TLS 1.2 by default; ensure it is
# enabled so real-world https://github.com downloads succeed (no-op for plain HTTP).
try {
    [System.Net.ServicePointManager]::SecurityProtocol = `
        [System.Net.ServicePointManager]::SecurityProtocol -bor [System.Net.SecurityProtocolType]::Tls12
} catch {
    # Newer PowerShell hosts manage TLS automatically; ignore if the enum is unavailable.
}

# Load the zip API (needed on Windows PowerShell 5.1; harmless on pwsh 7+).
try {
    Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction SilentlyContinue | Out-Null
} catch {
    # pwsh 7+ ships this in the default assembly load context.
}

function Get-ChecksumForAsset {
    param([string]$ChecksumsPath, [string]$Name)
    foreach ($line in [System.IO.File]::ReadAllLines($ChecksumsPath)) {
        $fields = ($line.Trim() -split '\s+') | Where-Object { $_ -ne "" }
        if ($fields.Count -lt 2) { continue }
        $entryName = $fields[$fields.Count - 1]
        if ($entryName.StartsWith('*')) { $entryName = $entryName.Substring(1) }
        if ($entryName -eq $Name) {
            return $fields[0].ToLower()
        }
    }
    return $null
}

$tmpRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("stet-install-" + [System.IO.Path]::GetRandomFileName())
New-Item -ItemType Directory -Force -Path $tmpRoot | Out-Null

try {
    # --- Resolve version when not pinned (mirrors install.sh releases/latest logic) ---
    if ([string]::IsNullOrEmpty($Version)) {
        if ($usePublicDownload) {
            if ($Prerelease) {
                $releases = Invoke-RestMethod -UseBasicParsing -Uri "https://api.github.com/repos/$resolvedRepo/releases?per_page=100"
                $sel = $releases | Where-Object { -not $_.draft } | Select-Object -First 1
                if ($null -eq $sel) { Die "no release found in $resolvedRepo" }
                $Version = $sel.tag_name
            } else {
                $latest = Invoke-RestMethod -UseBasicParsing -Uri "https://api.github.com/repos/$resolvedRepo/releases/latest"
                $Version = $latest.tag_name
            }
        } else {
            if ($Prerelease) {
                $jq = '.[] | select(.draft | not) | .tag_name'
            } else {
                $jq = '.[] | select((.draft | not) and (.prerelease | not)) | .tag_name'
            }
            $tags = & gh api "repos/$resolvedRepo/releases" --jq $jq
            if ($LASTEXITCODE -ne 0) { Die "failed to list releases in $resolvedRepo via gh" }
            $Version = ($tags | Select-Object -First 1)
        }
        if ([string]::IsNullOrEmpty($Version)) { Die "no stable release found in $resolvedRepo" }
    }

    $archivePath = Join-Path $tmpRoot $AssetName
    $checksumsPath = Join-Path $tmpRoot "checksums.txt"

    if ($usePublicDownload) {
        $assetUrl = "$resolvedBase/$resolvedRepo/releases/download/$Version/$AssetName"
        $checksumsUrl = "$resolvedBase/$resolvedRepo/releases/download/$Version/checksums.txt"
        Invoke-WebRequest -UseBasicParsing -Uri $assetUrl -OutFile $archivePath
        Invoke-WebRequest -UseBasicParsing -Uri $checksumsUrl -OutFile $checksumsPath
    } else {
        # gh release download is binary-safe (unlike piping gh api through PowerShell
        # redirection, which would corrupt the zip via text-mode encoding).
        & gh release download $Version --repo $resolvedRepo --pattern $AssetName --dir $tmpRoot --clobber
        if ($LASTEXITCODE -ne 0) { Die "release $Version is missing $AssetName" }
        & gh release download $Version --repo $resolvedRepo --pattern "checksums.txt" --dir $tmpRoot --clobber
        if ($LASTEXITCODE -ne 0) { Die "release $Version is missing checksums.txt" }
    }

    if (-not (Test-Path $archivePath)) { Die "failed to download $AssetName" }
    if (-not (Test-Path $checksumsPath)) { Die "failed to download checksums.txt" }

    # --- Verify SHA-256 against checksums.txt ---
    $expected = Get-ChecksumForAsset -ChecksumsPath $checksumsPath -Name $AssetName
    if ([string]::IsNullOrEmpty($expected)) { Die "checksums.txt has no entry for $AssetName" }
    $actual = (Get-FileHash -Algorithm SHA256 -Path $archivePath).Hash.ToLower()
    if ($actual -ne $expected) {
        Die "checksum mismatch for ${AssetName}: expected $expected, got $actual"
    }

    # --- Validate zip membership before extracting ---
    $tmpExtract = Join-Path $tmpRoot "stet.exe"
    $zip = [System.IO.Compression.ZipFile]::OpenRead($archivePath)
    try {
        if ($zip.Entries.Count -ne 1) {
            Die "archive must contain exactly one member named stet.exe"
        }
        $entry = $zip.Entries[0]
        # A directory entry has an empty Name and a FullName ending in '/', so the
        # exact-match on both fields also rejects directories and nested paths.
        if ($entry.FullName -ne "stet.exe" -or $entry.Name -ne "stet.exe") {
            Die "archive contains unsafe member: $($entry.FullName)"
        }
        $entryStream = $entry.Open()
        try {
            $outStream = [System.IO.File]::Create($tmpExtract)
            try {
                $entryStream.CopyTo($outStream)
            } finally {
                $outStream.Dispose()
            }
        } finally {
            $entryStream.Dispose()
        }
    } finally {
        $zip.Dispose()
    }

    # --- Atomic install into the resolved bin dir ---
    if (-not (Test-Path $resolvedBinDir)) {
        New-Item -ItemType Directory -Force -Path $resolvedBinDir | Out-Null
    }
    $binDirAbs = [System.IO.Path]::GetFullPath($resolvedBinDir)
    $target = Join-Path $binDirAbs "stet.exe"
    $tmpTarget = Join-Path $binDirAbs (".stet-install-" + [System.IO.Path]::GetRandomFileName() + ".tmp")
    Copy-Item -Path $tmpExtract -Destination $tmpTarget -Force
    # Move-Item -Force onto the final path. This can fail with a sharing violation if
    # the target stet.exe is currently running; that is an accepted limitation for a
    # fresh install.ps1 run (swap-on-exit retry lives in the Go self-update path).
    Move-Item -Path $tmpTarget -Destination $target -Force

    Write-Output "installed $Version to $target"
} catch {
    Die $_.Exception.Message
} finally {
    if (Test-Path $tmpRoot) {
        Remove-Item -Recurse -Force -Path $tmpRoot -ErrorAction SilentlyContinue
    }
}
