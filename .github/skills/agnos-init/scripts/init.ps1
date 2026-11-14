<#
.SYNOPSIS
  Adds AGNOS to a project: the block of its entry-point files, its guide and its process folders.
.DESCRIPTION
  RQ-INI-001 to RQ-INI-006, RQ-INI-019, RQ-PLG-004, RQ-PLG-021 / ADR-INI-001 (DEC-INI-001 to DEC-INI-003), ADR-INI-003 (DEC-INI-014), ADR-PLG-001 (DEC-PLG-003), ADR-PLG-003 (DEC-PLG-016), RQ-PLG-033 / ADR-PLG-005 (DEC-PLG-026).
  RQ-INI-016 / ADR-INI-002 (DEC-INI-012): the session state is added to .gitignore.
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
$BLOCK_TEMPLATE = 'agnos.block.md'   # RQ-INI-019 / DEC-INI-014: one block for every entry-point file
# RQ-PLG-036 / DEC-PLG-027: every name of the process folder comes from the generated agnos-layout.ps1.
. (Join-Path $PSScriptRoot 'agnos-layout.ps1')
$PROCESS_FOLDERS = @($AGNOS_SUBFOLDERS | ForEach-Object { "$AGNOS_FOLDER/$_" })
$README = 'readme.md'
$GUIDE = $AGNOS_GUIDE
$OWNED_FILES = @($AGNOS_GUIDE, $AGNOS_VERSION)  # RQ-PLG-033 / DEC-PLG-026: written into the process folder
$GITIGNORE = '.gitignore'
$SESSION_STATE = "$AGNOS_FOLDER/$AGNOS_SESSION_STATE"   # RQ-INI-016: kept out of git
# DEC-INI-002: one byte is one character, so that encodings and line endings pass through unchanged.
$BYTES = [System.Text.Encoding]::GetEncoding(28591)

function Read-Bytes([string]$Path) { return $BYTES.GetString([System.IO.File]::ReadAllBytes($Path)) }   # ReadAllText would consume a BOM

# RQ-PLG-033: the first line of a text, without its line ending.
function Get-FirstLine([string]$Text) { return ($Text -split "`n", 2)[0].TrimEnd("`r") }

function Get-Eol([string]$Text) {
  $at = $Text.IndexOf($LF)
  if ($at -gt 0 -and $Text[$at - 1] -eq "`r") { return $CRLF }
  return $LF
}

# RQ-INI-006, RQ-INI-019 / DEC-INI-014: the one template of every entry-point file, in the given line ending, with no final line ending.
function Get-Block([string]$Eol) {
  $template = Join-Path $PSScriptRoot "../assets/templates/$BLOCK_TEMPLATE"
  $text = (Read-Bytes $template).Replace($CRLF, $LF).TrimEnd($LF)
  return $text.Replace($LF, $Eol)
}

# RQ-INI-002, RQ-INI-004: what the file should hold and the action it takes.
function Get-Plan([string]$File, [string]$Path) {
  if (-not (Test-Path -LiteralPath $Path)) {
    return @{ Path = $Path; File = $File; Text = (Get-Block $LF) + $LF; Action = 'created'; Old = $null }
  }
  $old = Read-Bytes $Path
  $begins = [regex]::Matches($old, $BEGIN_PATTERN)
  $ends = [regex]::Matches($old, $END_PATTERN)
  $eol = Get-Eol $old
  $block = Get-Block $eol
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

# RQ-PLG-038 / DEC-PLG-031: whether git tracks a path of the project; no git, or no repository, means untracked.
function Test-Tracked([string]$Root, [string]$Path) {
  $ErrorActionPreference = 'Continue'
  try { & git -C $Root ls-files --error-unmatch -- $Path 2>&1 | Out-Null } catch { return $false }
  return $LASTEXITCODE -eq 0
}

# RQ-PLG-038 / DEC-PLG-031: renames with git mv when tracked, so that the history follows, with a plain rename otherwise.
function Move-ProcessPath([string]$Root, [string]$From, [string]$To) {
  if (Test-Tracked $Root $From) {
    $ErrorActionPreference = 'Continue'
    & git -C $Root mv -- $From $To 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "git mv $From $To failed" }
  } else {
    Move-Item -LiteralPath (Join-Path $Root $From) -Destination (Join-Path $Root $To)
  }
}

# RQ-INI-016 / DEC-INI-012: whether git's rules ignore the session state, tracked or not; outside a git repository,
# whether .gitignore holds its line.
function Test-Ignored([string]$Root, [string]$GitignoreText) {
  $ErrorActionPreference = 'Continue'
  $inRepository = $false
  try {
    & git -C $Root rev-parse --is-inside-work-tree 2>&1 | Out-Null
    $inRepository = $LASTEXITCODE -eq 0
  } catch { $inRepository = $false }
  if ($inRepository) {
    & git -C $Root check-ignore -q --no-index -- $SESSION_STATE 2>&1 | Out-Null
    return $LASTEXITCODE -eq 0
  }
  return @($GitignoreText -split $LF | ForEach-Object { $_.TrimEnd("`r") }) -ccontains $SESSION_STATE
}

try {
  $targetFull =[System.IO.Path]::GetFullPath([System.IO.Path]::Combine((Get-Location).Path, $Target))   # an absolute target stays as it is
  if (-not (Test-Path -LiteralPath $targetFull -PathType Container)) { throw "target folder not found: $Target" }
  $legacyIndex = Join-Path (Join-Path $targetFull $AGNOS_LEGACY_FOLDER) $AGNOS_LEGACY_INDEX
  $migrate = ($AGNOS_LEGACY_FOLDER -ne $AGNOS_FOLDER) -and (Test-Path -LiteralPath $legacyIndex -PathType Leaf)
  if ($migrate -and (Test-Path -LiteralPath (Join-Path $targetFull $AGNOS_FOLDER))) {
    throw "both $AGNOS_LEGACY_FOLDER/ and $AGNOS_FOLDER/ exist: keep one, then call agnos-init again"
  }
  $plans = @($ENTRY_FILES | ForEach-Object { Get-Plan $_ (Join-Path $targetFull $_) })
  if ($migrate) {
    Move-ProcessPath $targetFull $AGNOS_LEGACY_FOLDER $AGNOS_FOLDER
    if ($AGNOS_LEGACY_INDEX -ne $AGNOS_INDEX) {
      Move-ProcessPath $targetFull "$AGNOS_FOLDER/$AGNOS_LEGACY_INDEX" "$AGNOS_FOLDER/$AGNOS_INDEX"
    }
    Write-Output "$($REPORT_PREFIX)moved $AGNOS_LEGACY_FOLDER to $AGNOS_FOLDER"
  }
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
  # RQ-PLG-021, RQ-PLG-033 / DEC-PLG-016, DEC-PLG-026: AGNOS's own files, rewritten whole from their templates into the folder.
  foreach ($owned in $OWNED_FILES) {
    $ownedPath = Join-Path (Join-Path $targetFull $AGNOS_FOLDER) $owned
    $ownedBytes = [System.IO.File]::ReadAllBytes((Join-Path $PSScriptRoot "../assets/templates/$owned"))
    if (-not (Test-Path -LiteralPath $ownedPath)) {
      $ownedAction = 'created'
    } elseif ((Read-Bytes $ownedPath) -ceq $BYTES.GetString($ownedBytes)) {
      $ownedAction = 'unchanged'
    } else {
      $ownedAction = 'updated'
    }
    if ($ownedAction -ne 'unchanged') { [System.IO.File]::WriteAllBytes($ownedPath, $ownedBytes) }
    Write-Output "$REPORT_PREFIX$ownedAction $AGNOS_FOLDER/$owned"
  }
  # RQ-PLG-033 / DEC-PLG-026: a root guide a former init wrote goes; any other file of that name stays.
  $rootGuide = Join-Path $targetFull $GUIDE
  if (Test-Path -LiteralPath $rootGuide -PathType Leaf) {
    $template = Read-Bytes (Join-Path $PSScriptRoot "../assets/templates/$GUIDE")
    if ((Get-FirstLine (Read-Bytes $rootGuide)) -ceq (Get-FirstLine $template)) {
      Remove-Item -LiteralPath $rootGuide
      Write-Output "$($REPORT_PREFIX)moved $GUIDE to $AGNOS_FOLDER/$GUIDE"
    }
  }
  # RQ-INI-016 / DEC-INI-012: the session state is kept out of git, unless a rule already ignores it.
  $gitignorePath = Join-Path $targetFull $GITIGNORE
  $gitignoreExists = Test-Path -LiteralPath $gitignorePath -PathType Leaf
  $gitignoreText = ''
  if ($gitignoreExists) { $gitignoreText = Read-Bytes $gitignorePath }
  if (Test-Ignored $targetFull $gitignoreText) {
    $gitignoreAction = 'unchanged'
  } elseif (-not $gitignoreExists) {
    [System.IO.File]::WriteAllBytes($gitignorePath, $BYTES.GetBytes("$SESSION_STATE$LF"))
    $gitignoreAction = 'created'
  } else {
    $eol = Get-Eol $gitignoreText
    $text = $gitignoreText
    if ($text.Length -gt 0 -and -not $text.EndsWith($LF)) { $text += $eol }
    [System.IO.File]::WriteAllBytes($gitignorePath, $BYTES.GetBytes("$text$SESSION_STATE$eol"))
    $gitignoreAction = 'added'
  }
  Write-Output "$REPORT_PREFIX$gitignoreAction $GITIGNORE"
  exit 0
} catch {
  [Console]::Error.WriteLine("$REPORT_PREFIX$($_.Exception.Message)")
  exit 1
}
