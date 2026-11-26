<#
.SYNOPSIS
  Builds (or rebuilds) the demo repository next to this repository, optionally verifying it.
.DESCRIPTION
  RQ-DMO-020, RQ-DMO-010, RQ-DMO-021 / ADR-DMO-001 (DEC-DMO-002, DEC-DMO-006).
  Runs replay.ps1 with the skill's scenario and content and this working tree as the toolkit, records
  that the global git configuration was left unchanged, then runs verify.ps1 when -Verify is given.
  Exit code 0 on success, 1 otherwise.
.PARAMETER Demo    Target folder (default: sibling of this repository, agnos-demo).
.PARAMETER Verify  Run verify.ps1 after the build.
.PARAMETER SkipRebuild  Passed to verify.ps1 (skips the reproducibility rebuild).
#>
param(
  [string]$Demo,
  [switch]$Verify,
  [switch]$SkipRebuild
)

$ErrorActionPreference = 'Stop'

$DEMO_FOLDER_NAME = 'agnos-demo'
$BUILD_RECORD = '.git/agnos-demo-build.json'

$toolkit = (& git -C $PSScriptRoot rev-parse --show-toplevel).Trim()
$toolkit = [System.IO.Path]::GetFullPath($toolkit)
if (-not $Demo) { $Demo = Join-Path (Split-Path -Parent $toolkit) $DEMO_FOLDER_NAME }
$Demo = [System.IO.Path]::GetFullPath($Demo)
$scenario = Join-Path $PSScriptRoot '../assets/scenario.json'
$content = Join-Path $PSScriptRoot '../assets/content'

$globalBefore = (& git config --global --list | Out-String)
& powershell -NoProfile -File (Join-Path $PSScriptRoot 'replay.ps1') -Scenario $scenario -Content $content -Toolkit $toolkit -Target $Demo
if ($LASTEXITCODE -ne 0) { exit 1 }
$globalUnchanged = ($globalBefore -eq (& git config --global --list | Out-String))
$record = [pscustomobject]@{ globalConfigUnchanged = $globalUnchanged; head = (& git -C $Demo rev-parse HEAD).Trim() }
[System.IO.File]::WriteAllText((Join-Path $Demo $BUILD_RECORD), ($record | ConvertTo-Json), (New-Object System.Text.UTF8Encoding($false)))
Write-Output "agnos-meta-demo build: global git configuration unchanged: $globalUnchanged"

if ($Verify) {
  $arguments = @('-NoProfile', '-File', (Join-Path $PSScriptRoot 'verify.ps1'), '-Demo', $Demo, '-Toolkit', $toolkit)
  if ($SkipRebuild) { $arguments += '-SkipRebuild' }
  & powershell @arguments
  exit $LASTEXITCODE
}
exit 0
