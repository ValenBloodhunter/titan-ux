<#
.SYNOPSIS
Universal Windows PowerShell installer for Titan-UX and its 11 /titan-* wrapper skills.

.EXAMPLE
.\install.ps1 -Agent antigravity
.\install.ps1 -Agent all -Project
.\install.ps1 -CustomPath "C:\Temp\skills"
#>
param(
  [ValidateSet("all", "claude", "cursor", "antigravity", "gemini", "windsurf", "cline", "codex", "opencode", "copilot", "")]
  [string]$Agent = "all",
  [switch]$Project,
  [string]$CustomPath = "",
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

function Install-TitanToBase {
  param([string]$BaseDir)
  $MainDir = Join-Path $BaseDir "titan-ux"
  if ($DryRun) {
    Write-Host "  [DRY-RUN] Would install titan-ux + 11 wrappers -> $BaseDir"
    return
  }
  New-Item -ItemType Directory -Force -Path $MainDir | Out-Null
  Copy-Item -Force (Join-Path $ScriptDir "SKILL.md") $MainDir
  Copy-Item -Force (Join-Path $ScriptDir "LICENSE") $MainDir
  Copy-Item -Force (Join-Path $ScriptDir "requirements.txt") $MainDir

  foreach ($sub in @("references", "scripts")) {
    $DestSub = Join-Path $MainDir $sub
    if (Test-Path $DestSub) { Remove-Item -Recurse -Force $DestSub }
    Copy-Item -Recurse -Force (Join-Path $ScriptDir $sub) $DestSub
  }

  Get-ChildItem -Path (Join-Path $ScriptDir "skills") -Directory -Filter "titan-*" | ForEach-Object {
    $WrapperDest = Join-Path $BaseDir $_.Name
    New-Item -ItemType Directory -Force -Path $WrapperDest | Out-Null
    Copy-Item -Recurse -Force (Join-Path $_.FullName "*") $WrapperDest
  }
  Write-Host "  [OK] Installed titan-ux + 11 /titan-* wrappers -> $BaseDir"
}

if ($CustomPath) {
  Install-TitanToBase -BaseDir $CustomPath
  exit 0
}

$Targets = @{
  claude      = if ($Project) { @(".claude\skills") } else { @("$HOME\.claude\skills") }
  cursor      = if ($Project) { @(".cursor\skills") } else { @("$HOME\.cursor\skills") }
  antigravity = if ($Project) { @(".agents\skills") } else { @("$HOME\.gemini\config\skills") }
  gemini      = if ($Project) { @(".gemini\skills") } else { @("$HOME\.gemini\skills") }
  windsurf    = if ($Project) { @(".windsurf\skills") } else { @("$HOME\.codeium\windsurf\skills") }
  cline       = if ($Project) { @(".cline\skills") } else { @("$HOME\.cline\skills") }
  codex       = if ($Project) { @(".agents\skills") } else { @("$HOME\.codex\skills", "$HOME\.agents\skills") }
  opencode    = if ($Project) { @(".opencode\skills") } else { @("$HOME\.config\opencode\skills") }
  copilot     = if ($Project) { @(".github\skills") } else { @("$HOME\.copilot\skills") }
}

$ModeLabel = if ($Project) { "project" } else { "global" }
Write-Host "Installing Titan-UX ($ModeLabel mode)..."

$Selected = if ($Agent -eq "all" -or -not $Agent) { $Targets.Keys } else { @($Agent) }
$Seen = @{}
foreach ($key in $Selected) {
  foreach ($dir in $Targets[$key]) {
    if (-not $Seen.ContainsKey($dir)) {
      $Seen[$dir] = $true
      Install-TitanToBase -BaseDir $dir
    }
  }
}

Write-Host ""
Write-Host "Titan-UX ready. Open a new coding agent session and run /titan-ux or /titan-discover."
