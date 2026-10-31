<#
.SYNOPSIS
  Replays a scenario into a new git repository: the engine of the agnos-meta-demo skill.
.DESCRIPTION
  RQ-DMO-010, RQ-DMO-013, RQ-DMO-018, RQ-DMO-007, RQ-DMO-021 / ADR-DMO-001 (DEC-DMO-002, DEC-DMO-006).
  Creates <Target> as a git repository and replays the ordered steps of the scenario file. Identity and
  dates of each commit come from environment variables of the git process, so no git configuration is
  written outside <Target> and no remote is added. An existing <Target> is rebuilt only if this engine
  created it. Exit code 0 on success, 1 on error (message on the error stream).
.PARAMETER Scenario  Scenario JSON file (identities, steps).
.PARAMETER Content   Content library folder; paths in `add` are relative to it.
.PARAMETER Toolkit   Working tree of AGNOS whose agnos-index script runs on the target (RQ-MTA-005).
.PARAMETER Target    Folder of the repository to create.
#>
param(
  [Parameter(Mandatory = $true)][string]$Scenario,
  [Parameter(Mandatory = $true)][string]$Content,
  [Parameter(Mandatory = $true)][string]$Toolkit,
  [Parameter(Mandatory = $true)][string]$Target
)

$ErrorActionPreference = 'Stop'

$GIT_EXE = 'git'
$POWERSHELL_EXE = 'powershell'
$GENERATED_MARKER = 'agnos-demo-generated'
$MARKER_TEXT = 'created by the agnos-meta-demo skill (replay.ps1)'
$INDEX_SCRIPT = '.github/skills/agnos-index/scripts/build-index.ps1'
$INIT_SCRIPT = '.github/skills/agnos-init/scripts/init.ps1'
$INDEX_PATH = 'process/INDEX.idx.md'
$PLAN_PATH_PATTERN = '^process/3\.plan/PLAN-.*\.md$'
$PLAN_STATUS_PATTERN = '(?m)^- \*\*Status\*\*: .*$'
$PLAN_OPEN_STATUS = '- **Status**: Not Started'
$PLAN_VERIFICATION_PATTERN = '(?ms)^- \*\*Verification\*\*: .*?(?=^- \*\*Assumptions\*\*:)'
$PLAN_OPEN_VERIFICATION = "- **Verification**: Pending.`n"
$TASK_PLAN_GLOB = 'process/3.plan/PLAN-*.md'
$LOCAL_GIT_CONFIG = @{
  'core.autocrlf'     = 'false'
  'core.safecrlf'     = 'false'
  'commit.gpgsign'    = 'false'
  'core.hooksPath'    = '.git/no-hooks'
  'init.defaultBranch' = 'main'
}
$UTF8_NO_BOM = New-Object System.Text.UTF8Encoding($false)

function ConvertTo-ProcessArgument([string]$Value) {
  if ($Value -notmatch '[\s"]' -and $Value.Length -gt 0) { return $Value }
  return '"' + ($Value -replace '(\\*)"', '$1$1\"' -replace '(\\+)$', '$1$1') + '"'
}

# Runs a process and returns ExitCode, Output and Error; Environment adds variables to the child only.
function Invoke-Process([string]$File, [string[]]$Arguments, [string]$WorkDir, [hashtable]$Environment = @{}) {
  $info = New-Object System.Diagnostics.ProcessStartInfo
  $info.FileName = $File
  $info.Arguments = ($Arguments | ForEach-Object { ConvertTo-ProcessArgument $_ }) -join ' '
  $info.WorkingDirectory = $WorkDir
  $info.UseShellExecute = $false
  $info.RedirectStandardOutput = $true
  $info.RedirectStandardError = $true
  $info.StandardOutputEncoding = [System.Text.Encoding]::UTF8
  $info.StandardErrorEncoding = [System.Text.Encoding]::UTF8
  foreach ($key in $Environment.Keys) { $info.EnvironmentVariables[$key] = [string]$Environment[$key] }
  $process = [System.Diagnostics.Process]::Start($info)
  $stdout = $process.StandardOutput.ReadToEndAsync()
  $stderr = $process.StandardError.ReadToEnd()
  $process.WaitForExit()
  return [pscustomobject]@{ ExitCode = $process.ExitCode; Output = $stdout.Result; Error = $stderr }
}

function Invoke-Git([string[]]$Arguments, [string]$WorkDir, [hashtable]$Environment = @{}) {
  $result = Invoke-Process $GIT_EXE $Arguments $WorkDir $Environment
  if ($result.ExitCode -ne 0) {
    throw "git $($Arguments -join ' ') failed ($($result.ExitCode)): $($result.Error.Trim())"
  }
  return $result.Output
}

# A regex replacement string where '$' is literal.
function ConvertTo-LiteralReplacement([string]$Text) { return $Text.Replace('$', '$$') }

function Read-Text([string]$Path) { return [System.IO.File]::ReadAllText($Path, $UTF8_NO_BOM) }

function Write-Text([string]$Path, [string]$Text) {
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Path) | Out-Null
  [System.IO.File]::WriteAllText($Path, $Text, $UTF8_NO_BOM)
}

function Get-FullPath([string]$Path) { return [System.IO.Path]::GetFullPath($Path) }

function Assert-SafeTarget([string]$TargetFull) {
  $separator = [System.IO.Path]::DirectorySeparatorChar
  $roots = @($PSScriptRoot, $Content, $Scenario, $Toolkit) | ForEach-Object { Get-FullPath $_ }
  foreach ($root in $roots) {
    if ($root -eq $TargetFull -or $root.StartsWith($TargetFull.TrimEnd($separator) + $separator)) {
      throw "refusing to rebuild '$TargetFull': it contains the generator, the content or the toolkit"
    }
  }
  if ((Test-Path -LiteralPath $TargetFull) -and @(Get-ChildItem -LiteralPath $TargetFull -Force).Count) {   # an empty folder is free
    if (-not (Test-Path -LiteralPath (Join-Path $TargetFull ".git/$GENERATED_MARKER"))) {
      throw "refusing to rebuild '$TargetFull': it was not created by this engine (no $GENERATED_MARKER marker)"
    }
  }
}

function Initialize-Repository([string]$TargetFull, [string]$Branch) {
  # The folder's content is removed, not the folder: an editor that has the folder open locks it on Windows.
  if (Test-Path -LiteralPath $TargetFull) {
    Get-ChildItem -LiteralPath $TargetFull -Force | ForEach-Object { Remove-Item -LiteralPath $_.FullName -Recurse -Force }
  }
  New-Item -ItemType Directory -Force -Path $TargetFull | Out-Null
  Invoke-Git @('init', '-q', '-b', $Branch) $TargetFull | Out-Null
  foreach ($key in $LOCAL_GIT_CONFIG.Keys) { Invoke-Git @('config', '--local', $key, $LOCAL_GIT_CONFIG[$key]) $TargetFull | Out-Null }
  Write-Text (Join-Path $TargetFull ".git/$GENERATED_MARKER") $MARKER_TEXT
}

function Get-CommitEnvironment($Identities, $Step, [string]$Offset) {
  $identity = $Identities.($Step.by)
  if ($null -eq $identity) { throw "unknown identity '$($Step.by)' in step '$($Step.message)'" }
  $stamp = '{0}T{1}:00{2}' -f $Step.date, $Step.time, $Offset
  return @{
    GIT_AUTHOR_NAME = $Step.by; GIT_AUTHOR_EMAIL = $identity.email; GIT_AUTHOR_DATE = $stamp
    GIT_COMMITTER_NAME = $Step.by; GIT_COMMITTER_EMAIL = $identity.email; GIT_COMMITTER_DATE = $stamp
  }
}

function Add-ContentItem($Item, [string]$ContentFull, [string]$TargetFull) {
  $to = if ($Item -is [string]) { $Item } else { $Item.to }
  $from = if ($Item -is [string]) { $Item } else { $Item.from }
  $source = Join-Path $ContentFull $from
  if (-not (Test-Path -LiteralPath $source)) { throw "content file not found: $from" }
  $destination = Join-Path $TargetFull $to
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $destination) | Out-Null
  if ($to -match $PLAN_PATH_PATTERN) {
    $text = Read-Text $source
    $text = [regex]::Replace($text, $PLAN_STATUS_PATTERN, (ConvertTo-LiteralReplacement $PLAN_OPEN_STATUS))
    $text = [regex]::Replace($text, $PLAN_VERIFICATION_PATTERN, (ConvertTo-LiteralReplacement $PLAN_OPEN_VERIFICATION))
    Write-Text $destination $text
  } else {
    Copy-Item -LiteralPath $source -Destination $destination -Force
  }
}

function Edit-File($Edit, [string]$TargetFull) {
  $path = Join-Path $TargetFull $Edit.path
  $text = Read-Text $path
  $at = $text.IndexOf($Edit.find, [System.StringComparison]::Ordinal)
  if ($at -lt 0) { throw "text to edit not found in $($Edit.path): $($Edit.find)" }
  Write-Text $path ($text.Substring(0, $at) + $Edit.replace + $text.Substring($at + $Edit.find.Length))
}

function Close-Task([string]$TaskId, [string]$ContentFull, [string]$TargetFull) {
  $blockPattern = '(?ms)^### ' + [regex]::Escape($TaskId) + ':.*?(?=^### |\z)'
  $library = Get-ChildItem -Path (Join-Path $ContentFull $TASK_PLAN_GLOB) | Where-Object { (Read-Text $_.FullName) -match "(?m)^### $([regex]::Escape($TaskId)):" } | Select-Object -First 1
  if ($null -eq $library) { throw "task $TaskId not found in the content plans" }
  $final = [regex]::Match((Read-Text $library.FullName), $blockPattern).Value
  $finalStatus = [regex]::Match($final, $PLAN_STATUS_PATTERN).Value
  $finalVerification = [regex]::Match($final, $PLAN_VERIFICATION_PATTERN).Value
  $planPath = Join-Path $TargetFull "process/3.plan/$($library.Name)"
  $text = Read-Text $planPath
  $current = [regex]::Match($text, $blockPattern)
  if (-not $current.Success) { throw "task $TaskId not found in the built plan $($library.Name)" }
  $block = [regex]::Replace($current.Value, $PLAN_STATUS_PATTERN, (ConvertTo-LiteralReplacement $finalStatus))
  $block = [regex]::Replace($block, $PLAN_VERIFICATION_PATTERN, (ConvertTo-LiteralReplacement $finalVerification))
  Write-Text $planPath ($text.Substring(0, $current.Index) + $block + $text.Substring($current.Index + $current.Length))
}

function Add-Lines($Append, [string]$TargetFull) {
  $path = Join-Path $TargetFull $Append.path
  $existing = if (Test-Path -LiteralPath $path) { Read-Text $path } else { '' }
  if ($existing.Length -gt 0 -and -not $existing.EndsWith("`n")) { $existing += "`n" }
  Write-Text $path ($existing + (($Append.lines -join "`n") + "`n"))
}

function Update-Index([string]$TargetFull) {
  $result = Invoke-Process $POWERSHELL_EXE @('-NoProfile', '-File', (Join-Path (Get-FullPath $Toolkit) $INDEX_SCRIPT)) $TargetFull
  if ($result.ExitCode -ne 0) { throw "agnos-index failed ($($result.ExitCode)): $($result.Error.Trim())" }
}

# RQ-INI-008: the step's `init` is the toolkit path written in the block, valid from the target.
function Invoke-Init([string]$TargetFull, [string]$ToolkitPath) {
  $result = Invoke-Process $POWERSHELL_EXE @('-NoProfile', '-File', (Join-Path (Get-FullPath $Toolkit) $INIT_SCRIPT), '-Target', '.', '-Toolkit', $ToolkitPath) $TargetFull
  if ($result.ExitCode -ne 0) { throw "agnos-init failed ($($result.ExitCode)): $($result.Error.Trim())" }
}

function Save-Commit([string]$TargetFull, [string]$Message, [hashtable]$Environment) {
  Invoke-Git @('add', '-A') $TargetFull | Out-Null
  $pending = Invoke-Process $GIT_EXE @('diff', '--cached', '--quiet') $TargetFull
  if ($pending.ExitCode -eq 0) { throw "nothing to commit for '$Message'" }
  Invoke-Git @('commit', '-q', '--no-verify', '-m', $Message) $TargetFull $Environment | Out-Null
}

# DEC-DMO-007: a conflict of a merge is resolved on the generated files only: the index regenerated by its skill, a
# file given by the step's `resolveFiles` ({ path, from }, from the content library) taken whole.
function Resolve-Conflicts($Step, [string]$ContentFull, [string]$TargetFull) {
  $conflicts = @((Invoke-Git @('diff', '--name-only', '--diff-filter=U') $TargetFull) -split "`n" | Where-Object { $_ })
  foreach ($path in $conflicts) {
    if ($path -eq $INDEX_PATH) {
      Invoke-Git @('checkout', '--ours', '--', $path) $TargetFull | Out-Null
      Update-Index $TargetFull
    } else {
      $resolution = @($Step.resolveFiles) | Where-Object { $_ -and $_.path -eq $path } | Select-Object -First 1
      if ($null -eq $resolution) { throw "unresolved conflict in $path" }
      Copy-Item -LiteralPath (Join-Path $ContentFull $resolution.from) -Destination (Join-Path $TargetFull $path) -Force
    }
    Invoke-Git @('add', '--', $path) $TargetFull | Out-Null
  }
  $left = (Invoke-Git @('diff', '--name-only', '--diff-filter=U') $TargetFull).Trim()
  if ($left) { throw "conflicts left: $left" }
}

function Invoke-Step($Step, $Plan, [string]$ContentFull, [string]$TargetFull, [hashtable]$Labels) {
  switch ($Step.op) {
    'branch' {
      $arguments = @('checkout', '-q', '-b', $Step.name)
      if ($Step.from) {                                       # DEC-DMO-007: a fork at a labelled commit
        if (-not $Labels.ContainsKey($Step.from)) { throw "unknown label '$($Step.from)'" }
        $arguments += $Labels[$Step.from]
      }
      Invoke-Git $arguments $TargetFull | Out-Null
    }
    'merge' {
      $environment = Get-CommitEnvironment $Plan.identities $Step $Plan.utcOffset
      $into = if ($Step.into) { $Step.into } else { $Plan.defaultBranch }     # DEC-DMO-007: into a session branch too
      Invoke-Git @('checkout', '-q', $into) $TargetFull | Out-Null
      $merged = Invoke-Process $GIT_EXE @('merge', '-q', '--no-ff', '--no-verify', '-m', $Step.message, $Step.branch) $TargetFull $environment
      if ($merged.ExitCode -ne 0) {
        Resolve-Conflicts $Step $ContentFull $TargetFull
        Invoke-Git @('commit', '-q', '--no-verify', '-m', $Step.message) $TargetFull $environment | Out-Null
      }
    }
    'commit' {
      $environment = Get-CommitEnvironment $Plan.identities $Step $Plan.utcOffset
      if ($Step.init) { Invoke-Init $TargetFull $Step.init }
      foreach ($item in @($Step.add)) { if ($item) { Add-ContentItem $item $ContentFull $TargetFull } }
      foreach ($edit in @($Step.edits)) { if ($edit) { Edit-File $edit $TargetFull } }
      foreach ($taskId in @($Step.closeTasks)) { if ($taskId) { Close-Task $taskId $ContentFull $TargetFull } }
      foreach ($append in @($Step.appendLines)) { if ($append) { Add-Lines $append $TargetFull } }
      if ($Step.index) { Update-Index $TargetFull }
      Save-Commit $TargetFull $Step.message $environment
    }
    default { throw "unknown step op '$($Step.op)'" }
  }
  if ($Step.label) { $Labels[$Step.label] = (Invoke-Git @('rev-parse', 'HEAD') $TargetFull).Trim() }    # DEC-DMO-007
}

try {
  $targetFull = Get-FullPath $Target
  $contentFull = Get-FullPath $Content
  Assert-SafeTarget $targetFull
  $plan = Read-Text (Get-FullPath $Scenario) | ConvertFrom-Json
  Initialize-Repository $targetFull $plan.defaultBranch
  $labels = @{}
  foreach ($step in $plan.steps) { Invoke-Step $step $plan $contentFull $targetFull $labels }
  $count = (Invoke-Git @('rev-list', '--count', '--all') $targetFull).Trim()
  $head = (Invoke-Git @('rev-parse', '--short', 'HEAD') $targetFull).Trim()
  Write-Output "agnos-meta-demo replay: $count commits, HEAD $head, $targetFull"
  exit 0
} catch {
  [Console]::Error.WriteLine("agnos-meta-demo replay: $($_.Exception.Message)")
  exit 1
}
