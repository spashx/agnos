<#
.SYNOPSIS
  Adds AGNOS to a project: the block of its entry-point files and its process folders.
.DESCRIPTION
  RQ-INI-001 to RQ-INI-006, RQ-PLG-004 / ADR-INI-001 (DEC-INI-001 to DEC-INI-003), ADR-PLG-001 (DEC-PLG-003).
  Every entry-point file is checked before any write. Exit code 0 on success, 1 on error, with nothing
  written (message on the error stream). init.sh gives the same bytes.
.PARAMETER Target   Folder of the project.
#>
param(
  [Parameter(Mandatory = $true)][string]$Target
)

$ErrorActionPreference = 'Stop'

$REPORT_PREFIX = 'agnos-init: '
$BEGIN_PATTERN = '(?m)^<!-- AGNOS:BEGIN'
$END_PATTERN = '(?m)^<!-- AGNOS:END -->(?=\r?$)'
$LF = "`n"
$CRLF = "`r`n"
$ENTRY_FILES = @('CLAUDE.md', 'AGENTS.md')
$PROCESS_FOLDERS = @('process/1.requirements', 'process/2.architecture', 'process/3.plan', 'process/_sessionstate')
$README = 'readme.md'
# DEC-INI-002: one byte is one character, so that encodings and line endings pass through unchanged.
$BYTES = [System.Text.Encoding]::GetEncoding(28591)

function Read-Bytes([string]$Path) { return $BYTES.GetString([System.IO.File]::ReadAllBytes($Path)) }   # ReadAllText would consume a BOM

function Get-Eol([string]$Text) {
  $at = $Text.IndexOf($LF)
  if ($at -gt 0 -and $Text[$at - 1] -eq "`r") { return $CRLF }
  return $LF
}

# RQ-INI-006: the template, in the given line ending, with no final line ending.
function Get-Block([string]$File, [string]$Eol) {
  $template = Join-Path $PSScriptRoot "../assets/templates/$($File -replace '\.md$', '.block.md')"
  $text = (Read-Bytes $template).Replace($CRLF, $LF).TrimEnd($LF)
  return $text.Replace($LF, $Eol)
}

# RQ-INI-002, RQ-INI-004: what the file should hold and the action it takes.
function Get-Plan([string]$File, [string]$Path) {
  if (-not (Test-Path -LiteralPath $Path)) {
    return @{ Path = $Path; File = $File; Text = (Get-Block $File $LF) + $LF; Action = 'created'; Old = $null }
  }
  $old = Read-Bytes $Path
  $begins = [regex]::Matches($old, $BEGIN_PATTERN)
  $ends = [regex]::Matches($old, $END_PATTERN)
  $eol = Get-Eol $old
  $block = Get-Block $File $eol
  if ($begins.Count -eq 0 -and $ends.Count -eq 0) {
    $text = $old
    if ($text.Length -gt 0) {
      if (-not $text.EndsWith($LF)) { $text += $eol }
      $text += $eol
    }
    return @{ Path = $Path; File = $File; Text = $text + $block + $eol; Action = 'added'; Old = $old }
  }
  if ($begins.Count -ne 1 -or $ends.Count -ne 1 -or $ends[0].Index -lt $begins[0].Index) {
    throw "$File holds a damaged AGNOS block: repair its BEGIN and END lines, then call agnos-init again"
  }
  $after = $ends[0].Index + $ends[0].Length
  $text = $old.Substring(0, $begins[0].Index) + $block + $old.Substring($after)
  return @{ Path = $Path; File = $File; Text = $text; Action = 'updated'; Old = $old }
}

try {
  $targetFull = [System.IO.Path]::GetFullPath([System.IO.Path]::Combine((Get-Location).Path, $Target))   # an absolute target stays as it is
  if (-not (Test-Path -LiteralPath $targetFull -PathType Container)) { throw "target folder not found: $Target" }
  $plans = @($ENTRY_FILES | ForEach-Object { Get-Plan $_ (Join-Path $targetFull $_) })
  foreach ($plan in $plans) {
    if ($plan.Text -ceq $plan.Old) {                          # RQ-INI-003
      Write-Output "$($REPORT_PREFIX)unchanged $($plan.File)"
    } else {
      [System.IO.File]::WriteAllBytes($plan.Path, $BYTES.GetBytes($plan.Text))
      Write-Output "$REPORT_PREFIX$($plan.Action) $($plan.File)"
    }
  }
  foreach ($folder in $PROCESS_FOLDERS) {                     # RQ-INI-005
    $path = Join-Path $targetFull $folder
    if (-not (Test-Path -LiteralPath $path)) {
      New-Item -ItemType Directory -Path $path | Out-Null
      $template = Join-Path $PSScriptRoot "../assets/templates/$(Split-Path -Leaf $folder).$README"
      [System.IO.File]::WriteAllBytes((Join-Path $path $README), [System.IO.File]::ReadAllBytes($template))
      Write-Output "$($REPORT_PREFIX)created $folder"
    }
  }
  exit 0
} catch {
  [Console]::Error.WriteLine("$REPORT_PREFIX$($_.Exception.Message)")
  exit 1
}
