# Tests of build-index.ps1 against the shared fixtures and expected files.
# Covers RQ-IDX-001 to RQ-IDX-009, RQ-IDX-015 and RQ-IDX-018 (ADR-IDX-001, DEC-IDX-004).
# RQ-PLG-048, RQ-PLG-049 / DEC-PLG-039: the nominal fixture holds IDs in 0.facts/ and 4.knowledge/, absent from its expected index.
# Usage: powershell -NoProfile -File .github/skills/agnos-index/tests/test-build-index.ps1
$ErrorActionPreference = 'Stop'

# RQ-PLG-036 / DEC-PLG-027: the folder and the index's name come from the skill's layout copy; the fixtures and expected
# files are written for a folder named $FixtureFolder, which each scenario renames to the layout's.
$Here = $PSScriptRoot
$Scripts = Join-Path $Here '..\scripts'
$Script = Join-Path $Scripts 'build-index.ps1'
. (Join-Path $Scripts 'agnos-layout.ps1')
$FixtureFolder = 'process'
$OtherFolder = 'other-folder'
$OtherIndex = 'other.idx.md'
$OutFile = '.out'
$ErrFile = '.err'
$ExpectedFile = '.expected'
$OldTime = [datetime]'2000-01-01'
$ReportPrefix = 'agnos-index: '
$DurationSuffixRx = ' in \d+\.\d{3} s$'   # RQ-IDX-018
$script:Failures = 0

# The expected strings and paths for a folder and an index name (RQ-PLG-036).
function Set-Layout([string]$Folder, [string]$Index) {
    $script:Folder = $Folder
    $script:IndexRel = "$Folder/$Index"
    $script:ExpectedNominalReport = "agnos-index: 13 entries, 6 documents, $($script:IndexRel)"
    $script:ExpectedDuplicateReport = "agnos-index: 3 entries, 1 documents, $($script:IndexRel) updated"
    $script:ExpectedDuplicateError = "agnos-index: DUPLICATE RQ-DUP-001 $Folder/1.requirements/FTR-DUP-001.md:5 (first: $Folder/1.requirements/FTR-DUP-001.md:3)"
    $script:ExpectedMissingError = "agnos-index: '$Folder' folder not found - run from the repository root, or call agnos-init to add AGNOS to this project"
}

# An expected index with its document paths under the current folder, bytes otherwise unchanged (RQ-PLG-036).
function Get-Expected([string]$Dir, [string]$Name) {
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    $text = [IO.File]::ReadAllText((Join-Path $Here "expected\$Name.idx.md"), $utf8)
    $path = Join-Path $Dir $ExpectedFile
    [IO.File]::WriteAllText($path, ($text -creplace "(?m)^@$FixtureFolder/", "@$($script:Folder)/"), $utf8)
    $path
}

function New-Scenario([string]$Fixture) {
    $dir = Join-Path ([IO.Path]::GetTempPath()) ('agnos-index-' + [guid]::NewGuid())
    New-Item -ItemType Directory -Path $dir | Out-Null
    if ($Fixture) { Copy-Item -Recurse -LiteralPath (Join-Path $Here "fixtures\$Fixture\$FixtureFolder") -Destination (Join-Path $dir $script:Folder) }
    $dir
}

Set-Layout $AGNOS_FOLDER $AGNOS_INDEX

function Invoke-Generator([string]$Dir) {
    $p = Start-Process -FilePath 'powershell' -ArgumentList "-NoProfile -File `"$Script`"" -WorkingDirectory $Dir `
        -RedirectStandardOutput (Join-Path $Dir $OutFile) -RedirectStandardError (Join-Path $Dir $ErrFile) -Wait -PassThru -NoNewWindow
    @{
        Code = $p.ExitCode
        Out  = ([IO.File]::ReadAllText((Join-Path $Dir $OutFile))).TrimEnd()
        Report = (([IO.File]::ReadAllText((Join-Path $Dir $OutFile))).TrimEnd()) -replace $DurationSuffixRx, ''   # RQ-IDX-018
        Err  = ([IO.File]::ReadAllText((Join-Path $Dir $ErrFile))).TrimEnd()
    }
}

function Test-SameBytes([string]$Actual, [string]$Expected) {
    (Test-Path -LiteralPath $Actual) -and
        ([Convert]::ToBase64String([IO.File]::ReadAllBytes($Actual)) -ceq [Convert]::ToBase64String([IO.File]::ReadAllBytes($Expected)))
}

function Assert-That([string]$Name, [bool]$Condition) {
    if ($Condition) { "PASS $Name" } else { "FAIL $Name"; $script:Failures++ }
}

# Scenario: nominal documents
$dir = New-Scenario 'nominal'
$index = Join-Path $dir $IndexRel
$r = Invoke-Generator $dir
Assert-That 'Given nominal documents When indexing Then the exit code is 0 [RQ-IDX-009]' ($r.Code -eq 0)
Assert-That 'Given nominal documents When indexing Then the index equals the expected bytes [RQ-IDX-001..006, RQ-IDX-015]' `
    (Test-SameBytes $index (Get-Expected $dir 'nominal'))
Assert-That 'Given nominal documents When indexing Then the report says updated [RQ-IDX-009]' ($r.Report -ceq "$ExpectedNominalReport updated")
Assert-That 'Given nominal documents When indexing Then the single report line ends with the duration [RQ-IDX-018]' `
    (($r.Out -cmatch $DurationSuffixRx) -and ($r.Out -notmatch "`n"))
Assert-That 'Given nominal documents When indexing Then the index holds no duration [RQ-IDX-018]' `
    (-not ([IO.File]::ReadAllText($index) -cmatch ' in \d+\.\d{3} s'))
(Get-Item -LiteralPath $index).LastWriteTime = $OldTime
$r = Invoke-Generator $dir
Assert-That 'Given an up-to-date index When indexing again Then the report says unchanged [RQ-IDX-009]' ($r.Report -ceq "$ExpectedNominalReport unchanged")
Assert-That 'Given an up-to-date index When indexing again Then the file is not rewritten [RQ-IDX-009]' `
    ((Get-Item -LiteralPath $index).LastWriteTime -eq $OldTime)
Remove-Item -Recurse -Force -LiteralPath $dir

# Scenario: duplicate definitions
$dir = New-Scenario 'duplicate'
$r = Invoke-Generator $dir
Assert-That 'Given a duplicate ID When indexing Then the exit code is 2 [RQ-IDX-007]' ($r.Code -eq 2)
Assert-That 'Given a duplicate ID When indexing Then the duplicate is reported [RQ-IDX-007]' ($r.Err -ceq $ExpectedDuplicateError)
Assert-That 'Given a duplicate ID When indexing Then the index is still written [RQ-IDX-007, RQ-IDX-015]' `
    (Test-SameBytes (Join-Path $dir $IndexRel) (Get-Expected $dir 'duplicate'))
Assert-That 'Given a duplicate ID When indexing Then the report line is printed [RQ-IDX-009]' ($r.Report -ceq $ExpectedDuplicateReport)
Remove-Item -Recurse -Force -LiteralPath $dir

# Scenario: no process folder
$dir = New-Scenario ''
$r = Invoke-Generator $dir
Assert-That 'Given no process folder When indexing Then the exit code is 1 [RQ-IDX-008]' ($r.Code -eq 1)
Assert-That 'Given no process folder When indexing Then the error is reported [RQ-IDX-008]' ($r.Err -ceq $ExpectedMissingError)
Assert-That 'Given no process folder When indexing Then nothing is written [RQ-IDX-008]' `
    (-not (Test-Path -LiteralPath (Join-Path $dir $Folder)) -and -not $r.Out.StartsWith($ReportPrefix))
Remove-Item -Recurse -Force -LiteralPath $dir

# Scenario: a layout naming another folder and index (RQ-PLG-036, TASK-PLG-040)
$skill = Join-Path ([IO.Path]::GetTempPath()) ('agnos-index-skill-' + [guid]::NewGuid())
New-Item -ItemType Directory -Path (Join-Path $skill 'scripts') | Out-Null
Copy-Item -LiteralPath $Script -Destination (Join-Path $skill 'scripts')
$layoutText = [IO.File]::ReadAllText((Join-Path $Scripts 'agnos-layout.ps1')) `
    -creplace '(?m)^\$AGNOS_FOLDER = .*$', "`$AGNOS_FOLDER = '$OtherFolder'" -creplace '(?m)^\$AGNOS_INDEX = .*$', "`$AGNOS_INDEX = '$OtherIndex'"
[IO.File]::WriteAllText((Join-Path $skill 'scripts\agnos-layout.ps1'), $layoutText)
$Script = Join-Path $skill 'scripts\build-index.ps1'
Set-Layout $OtherFolder $OtherIndex
$dir = New-Scenario 'nominal'
$r = Invoke-Generator $dir
Assert-That 'Given a layout naming another folder When indexing Then its index holds the same entries under that folder [RQ-PLG-036]' `
    (($r.Code -eq 0) -and (Test-SameBytes (Join-Path $dir $IndexRel) (Get-Expected $dir 'nominal')))
Assert-That 'Given a layout naming another folder When indexing Then the report names its index [RQ-PLG-036]' ($r.Report -ceq "$ExpectedNominalReport updated")
Remove-Item -Recurse -Force -LiteralPath $dir, $skill

if ($script:Failures -gt 0) { "$($script:Failures) check(s) failed"; exit 1 }
'All checks passed'
exit 0
