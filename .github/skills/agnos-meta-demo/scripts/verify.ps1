<#
.SYNOPSIS
  Checks the demo repository against the requirements RQ-DMO-001 to RQ-DMO-027.
.DESCRIPTION
  RQ-DMO-020, RQ-DMO-019, RQ-DMO-008, RQ-DMO-001, RQ-DMO-027 / ADR-DMO-001 (DEC-DMO-005, DEC-DMO-006);
  RQ-DMO-023 to RQ-DMO-026 / ADR-DMO-002 (DEC-DMO-008, DEC-DMO-009).
  Prints one PASS or FAIL line per requirement and exits with 0 when all pass, 1 otherwise.
.PARAMETER Demo         Folder of the demo repository (default: sibling of the toolkit).
.PARAMETER Toolkit      Working tree of the AGNOS repository (default: the one holding this script).
.PARAMETER Scenario     Scenario JSON file (default: the skill's).
.PARAMETER BaseRef      Optional git ref; RQ-DMO-010 then checks the toolkit changes since it.
.PARAMETER SkipRebuild  Skip the second build used by RQ-DMO-021.
#>
param(
  [string]$Demo,
  [string]$Toolkit,
  [string]$Scenario,
  [string]$BaseRef,
  [switch]$SkipRebuild
)

$ErrorActionPreference = 'Stop'

$DEMO_FOLDER_NAME = 'agnos-lightweight-process.demo'
# RQ-PLG-034, RQ-PLG-036 / DEC-PLG-027: the process folder's names come from the generated agnos-layout.ps1
. (Join-Path $PSScriptRoot 'agnos-layout.ps1')
$PF = [regex]::Escape($AGNOS_FOLDER)
$SKILL_NAME = 'agnos-meta-demo'
$TOOLKIT_PATTERN = '^(\.github/|\.claude/|(CHANGELOG|CONTRIBUTING|LICENSE|SECURITY|CODE_OF_CONDUCT)\.md$|GETTING_STARTED\.MD$|assets/agnos-overview\.png$)'   # RQ-MTA-005, RQ-INI-008; TASK-PLG-076: the image under assets/
$INIT_SCRIPT = '.github/skills/agnos-init/scripts/init.ps1'
$INIT_FILES = @('CLAUDE.md', 'AGENTS.md')
$BLOCK_BEGIN = '<!-- AGNOS:BEGIN'
$BLOCK_END = '<!-- AGNOS:END -->'
$INDEX_SCRIPT = '.github/skills/agnos-index/scripts/build-index.ps1'
$BUILD_RECORD = '.git/agnos-demo-build.json'
$FIELD_SEPARATOR = [string][char]0x1f
$ROLE_PATTERN = '^[a-z]+-(pm|ux|tech)$'             # RQ-DMO-011 as amended on 2026-11-12: the Acme team (DEC-DMO-003)
$HUMAN_MAIL_DOMAIN = '@acme.example'                 # RQ-DMO-011, DEC-DMO-003
$EXPECTED_ROLES = [ordered]@{ pm = 1; ux = 1; tech = 2 }   # RQ-DMO-011: one pm, one ux, two tech
$FILTER_ROLE = 'tech'                                # RQ-DMO-009, RQ-DMO-011: the README's filter example
$ID_PATTERN = '\b(?:FTR|RQ|ADR|DEC|PLAN|TASK)-[A-Z]{3}-\d{3}\b'
$DEFINITION_PATTERN = '^\+#{1,3} ((?:FTR|RQ|ADR|DEC|PLAN|TASK)-[A-Z]{3}-\d{3}):'
$TOOLKIT_TRIGRAMS = 'TRC|IDX|DSY|AGT|FIX|DMO|MTA|INI|QLT'
$TASK_COMMIT_PATTERN = '^(feat|fix|docs|refactor|test|chore|perf|build|ci|style)\([A-Z]{3}\): (ADR-[A-Z]{3}-\d{3}/)?TASK-[A-Z]{3}-\d{3} .+$'
$MIN_FEATURES = 3; $MIN_REQUIREMENTS = 12; $MIN_ADRS = 3; $MIN_PLANS = 3; $MIN_SOURCES = 4
$MIN_COMMITS = 50; $MIN_SPAN_DAYS = 56; $MAX_SPAN_DAYS = 64; $MIN_ACTIVE_DAYS = 5; $MAX_ACTIVE_RATIO = 0.8
$MIN_SESSIONS = 3; $MIN_HOLIDAYS = 2
$LITERAL_REPEAT_LIMIT = 3; $LITERAL_MIN_LENGTH = 8
$REBUILD_FOLDER_PREFIX = 'agnos-demo-verify-'
$FULL_SCORE = '10.0'; $NO_SCORE = 'n/a'
# RQ-DMO-023 to RQ-DMO-026 / ADR-DMO-002 (DEC-DMO-008, DEC-DMO-009)
$AGENT_KIND = 'agent'
$TRAILER_FORMAT = '%(trailers:key=Co-Authored-By,valueonly,separator=%x1d)'
$TRAILER_SEPARATOR = [string][char]0x1d
$CLAUDE_HARNESS = 'Claude Code/'; $COPILOT_HARNESS = 'Copilot SDK in VS Code/'
$CLAUDE_OPUS = 'Claude Code/Claude Opus 5.5'; $CLAUDE_SONNET = 'Claude Code/Claude Sonnet 5.5'; $CLAUDE_HAIKU = 'Claude Code/Claude Haiku 5.5'
$MIN_TOGETHER_RATIO = 0.55; $MAX_TOGETHER_RATIO = 0.8; $MIN_HUMAN_RATIO = 0.2   # RQ-DMO-023 as amended on 2026-11-12
$MIN_PERSON_AGENT_RATIO = 0.6                        # RQ-DMO-023: each human works mostly with an agent (DEC-DMO-009)
$MIN_HARNESS_COMMITS = 5; $MIN_MAIN_MODEL_COMMITS = 3; $MIN_HAIKU_COMMITS = 1; $MAX_HAIKU_COMMITS = 2
$MIN_AGENT_ONLY = 3; $MAX_AGENT_ONLY = 6; $EXPECTED_AGENTS = 4
$MIN_FUNCTION_SCORE = 8.5; $MAX_FUNCTION_SCORE = 10.0; $FUNCTION_CHECK = 'functions-traced'
$HISTORY_SUMMARY_PATTERN = 'history: (\d+) commits, (\d+) humans, (\d+) agents'
$UI_ARTIFACTS = @('FTR-DSN-001', 'ADR-DSN-001', 'PLAN-DSN-001', 'FTR-WEB-001', 'ADR-WEB-001', 'PLAN-WEB-001')   # RQ-DMO-022
# RQ-DMO-027: the README's commands of the product, run as written, on the defaults they rely on
$SERVICE_COMMAND = 'cd service && python -m roombook'; $UI_COMMAND = 'cd client && npm run ui'; $CLI_COMMAND = 'cd client && node src/cli.ts rooms'
$ROOMS_FILE = 'service/rooms.json'; $UI_ENTRY = 'src/ui/server.ts'; $CLI_ENTRY = 'src/cli.ts'; $CLI_ROOMS = 'rooms'
$SERVICE_ROOMS_URL = 'http://127.0.0.1:8080/rooms'; $UI_URL = 'http://127.0.0.1:3000/'
$RUN_WAIT_SECONDS = 15; $RUN_POLL_MS = 500; $HTTP_OK = 200
$ROLE_BY_PATH = @(
  # RQ-DMO-012 as amended on 2026-11-12 (DEC-DMO-003)
  @{ Pattern = "^$PF/1\.requirements/FTR-"; Role = 'pm' }
  @{ Pattern = "^$PF/2\.architecture/ADR-"; Role = 'tech' }
  @{ Pattern = "^$PF/3\.plan/PLAN-"; Role = 'tech' }
  @{ Pattern = '^service/roombook/.+\.py$'; Role = 'tech' }
  @{ Pattern = '^client/src/.+\.ts$'; Role = 'tech' }
  @{ Pattern = '^service/tests/test_.+\.py$'; Role = 'tech' }
  @{ Pattern = '^client/tests/.+\.test\.ts$'; Role = 'tech' }
  @{ Pattern = '^client/design/'; Role = 'ux' }               # DEC-DMO-007
)

if (-not $Toolkit) { $Toolkit = (& git -C $PSScriptRoot rev-parse --show-toplevel).Trim() }
$Toolkit = [System.IO.Path]::GetFullPath($Toolkit)
if (-not $Demo) { $Demo = Join-Path (Split-Path -Parent $Toolkit) $DEMO_FOLDER_NAME }
$Demo = [System.IO.Path]::GetFullPath($Demo)
if (-not $Scenario) { $Scenario = Join-Path $PSScriptRoot '../assets/scenario.json' }
$plan = [System.IO.File]::ReadAllText([System.IO.Path]::GetFullPath($Scenario)) | ConvertFrom-Json

$results = New-Object System.Collections.ArrayList
function Report([string]$Id, [bool]$Ok, [string]$Detail) {
  [void]$results.Add([pscustomobject]@{ Id = $Id; Ok = $Ok; Detail = $Detail })
  Write-Output ('{0} {1} {2}' -f $(if ($Ok) { 'PASS' } else { 'FAIL' }), $Id, $Detail)
}
function Demo-Git([string[]]$GitArgs) { return @(& git -C $Demo -c core.quotepath=false @GitArgs) }
function Demo-Git-Ok([string[]]$GitArgs) { & git -C $Demo @GitArgs *> $null; return ($LASTEXITCODE -eq 0) }
function Get-Tracked([string]$Repo) { return @(& git -C $Repo -c core.quotepath=false ls-files) }
function Show-Failures([string[]]$Problems) { return ($Problems | Select-Object -First 5) -join '; ' }

# --- history of the demo -------------------------------------------------------------------------------
$logFormat = (@('%H', '%P', '%an', '%ae', '%cn', '%ce', '%aI', '%cI', '%ct', '%s', $TRAILER_FORMAT) -join '%x1f')
$commits = @(Demo-Git @('log', '--all', '--reverse', '--topo-order', "--format=$logFormat") | ForEach-Object {
  $f = $_ -split $FIELD_SEPARATOR
  [pscustomobject]@{ Hash = $f[0]; Parents = @($f[1] -split ' ' | Where-Object { $_ }); AuthorName = $f[2]; AuthorEmail = $f[3]
    CommitterName = $f[4]; CommitterEmail = $f[5]; AuthorDate = $f[6]; CommitterDate = $f[7]; Epoch = [long]$f[8]; Subject = $f[9]
    CoAuthors = @($f[10] -split $TRAILER_SEPARATOR | Where-Object { $_ })                                  # RQ-DMO-024
    Day = [datetime]::ParseExact($f[6].Substring(0, 10), 'yyyy-MM-dd', $null); Time = $f[6].Substring(11, 5); Offset = $f[6].Substring(19) }
})
$plainCommits = @($commits | Where-Object { $_.Parents.Count -le 1 })
# RQ-DMO-023 to RQ-DMO-025 / DEC-DMO-008: the agents are the scenario's identities of kind agent
$agentNames = @($plan.identities.PSObject.Properties | Where-Object { $_.Value.kind -eq $AGENT_KIND } | ForEach-Object { $_.Name })
$agentTrailers = @($plan.identities.PSObject.Properties | Where-Object { $_.Value.kind -eq $AGENT_KIND } | ForEach-Object { "$($_.Name) <$($_.Value.email)>" })
$humanCommits = @($commits | Where-Object { $agentNames -notcontains $_.AuthorName })
$holidayDates = @($plan.holidays | ForEach-Object { $_.date })
$periodStart = [datetime]::ParseExact($plan.period.start, 'yyyy-MM-dd', $null)
$periodEnd = [datetime]::ParseExact($plan.period.end, 'yyyy-MM-dd', $null)
$workingDays = @(for ($d = $periodStart; $d -le $periodEnd; $d = $d.AddDays(1)) {
  if ($d.DayOfWeek -notin 'Saturday', 'Sunday' -and $holidayDates -notcontains $d.ToString('yyyy-MM-dd')) { $d }
})
$demoFiles = Get-Tracked $Demo
$planTasks = @($demoFiles | Where-Object { $_ -match "^$PF/3\.plan/PLAN-.*\.md$" } | ForEach-Object {
  $text = Demo-Git @('show', "HEAD:$_") | Out-String
  [regex]::Matches($text, '(?ms)^### (TASK-[A-Z]{3}-\d{3}):.*?(?=^### |\z)') | ForEach-Object {
    $b = $_.Value
    [pscustomobject]@{ Id = $_.Groups[1].Value; Tier = [regex]::Match($b, '\*\*Tier\*\*: (\w)').Groups[1].Value
      Verification = [regex]::Match($b, '(?ms)\*\*Verification\*\*: (.*?)(?=^- \*\*Assumptions)').Groups[1].Value.Trim()
      Assumptions = [regex]::Match($b, '(?ms)\*\*Assumptions\*\*: (.*)').Groups[1].Value.Trim() } }
})

# RQ-DMO-001
$top = (Demo-Git @('rev-parse', '--show-toplevel') | Select-Object -First 1)
$topFull = [System.IO.Path]::GetFullPath($top)
Report 'RQ-DMO-001' ((Test-Path -LiteralPath $Demo) -and ($topFull -eq $Demo) -and ((Split-Path -Leaf $Demo) -eq $DEMO_FOLDER_NAME) -and ((Split-Path -Parent $Demo) -eq (Split-Path -Parent $Toolkit))) "sibling independent repository at $Demo"

# RQ-DMO-002
$toolkitInHistory = @(Demo-Git @('log', '--all', '--name-only', '--format=') | Where-Object { $_ -match $TOOLKIT_PATTERN } | Sort-Object -Unique)   # RQ-MTA-005
$foreignIds = @(& git -C $Demo grep -nE "(FTR|RQ|ADR|DEC|PLAN|TASK)-($TOOLKIT_TRIGRAMS)-[0-9]{3}")
Report 'RQ-DMO-002' (($toolkitInHistory.Count -eq 0) -and ($foreignIds.Count -eq 0)) "toolkit files in the history: $($toolkitInHistory.Count); toolkit IDs in the tree: $($foreignIds.Count)"

# RQ-DMO-003
$py = @($demoFiles | Where-Object { $_ -match '^service/roombook/.+\.py$' })
$ts = @($demoFiles | Where-Object { $_ -match '^client/src/.+\.ts$' })
Report 'RQ-DMO-003' (($py.Count -ge $MIN_SOURCES) -and ($ts.Count -ge $MIN_SOURCES) -and ($demoFiles -contains 'service/pyproject.toml') -and ($demoFiles -contains 'client/package.json')) "python sources: $($py.Count); typescript sources: $($ts.Count); manifests present"

# RQ-DMO-004
$codeFiles = @($demoFiles | Where-Object { $_ -match '^(service|client)/.+\.(py|ts)$' })
$problems = New-Object System.Collections.ArrayList
foreach ($file in $codeFiles) {
  $text = [System.IO.File]::ReadAllText((Join-Path $Demo $file))
  if ($text.Length -eq 0) { continue }
  if ($text -notmatch 'RQ-[A-Z]{3}-\d{3}') { [void]$problems.Add("$file cites no RQ") }
  $isTest = $file -match '/tests/'
  if ($isTest -and $file -match 'test_.+\.py$' -and $text -notmatch 'def test_given_\w+_when_\w+_then_\w+') { [void]$problems.Add("$file has no Gherkin-named test") }
  if ($isTest -and $file -match '\.test\.ts$' -and $text -notmatch 'test\("given .+ when .+ then') { [void]$problems.Add("$file has no Gherkin-named test") }
  if (-not $isTest) {
    $literals = [regex]::Matches($text, '"([^"\\\r\n]{' + $LITERAL_MIN_LENGTH + ',})"') | Group-Object { $_.Groups[1].Value } | Where-Object { $_.Count -ge $LITERAL_REPEAT_LIMIT }
    foreach ($l in $literals) { [void]$problems.Add("$file repeats the literal `"$($l.Name)`" $($l.Count) times") }
  }
}
$untested = @($planTasks | Where-Object { $_.Tier -in 'M', 'L' } | Where-Object { $id = $_.Id; -not (@($plainCommits | Where-Object { $_.Subject -match "^test\(" -and $_.Subject -match [regex]::Escape($id) })).Count })
foreach ($t in $untested) { [void]$problems.Add("$($t.Id) has no test commit") }
Report 'RQ-DMO-004' ($problems.Count -eq 0) $(if ($problems.Count) { Show-Failures $problems } else { "$($codeFiles.Count) code files cite RQs, tests are Gherkin-named, no repeated literal, every M/L task has a test commit" })

# RQ-DMO-005
$ftrs = @($demoFiles | Where-Object { $_ -match "^$PF/1\.requirements/FTR-" })
$adrs = @($demoFiles | Where-Object { $_ -match "^$PF/2\.architecture/ADR-" })
$plans = @($demoFiles | Where-Object { $_ -match "^$PF/3\.plan/PLAN-" })
$allProcessText = ($demoFiles | Where-Object { $_ -match "^$PF/[123]\." } | ForEach-Object { Demo-Git @('show', "HEAD:$_") }) -join "`n"
$rqCount = ([regex]::Matches($allProcessText, '(?m)^### RQ-[A-Z]{3}-\d{3}:')).Count
$adrOk = @($adrs | Where-Object { $t = (Demo-Git @('show', "HEAD:$_")) -join "`n"; $t -match '(?m)^### DEC-' -and $t -match '```mermaid' }).Count
$defined = @([regex]::Matches($allProcessText, '(?m)^#{1,3} ((?:FTR|RQ|ADR|DEC|PLAN|TASK)-[A-Z]{3}-\d{3}):') | ForEach-Object { $_.Groups[1].Value })
$duplicates = @($defined | Group-Object | Where-Object { $_.Count -gt 1 })
Report 'RQ-DMO-005' (($ftrs.Count -ge $MIN_FEATURES) -and ($rqCount -ge $MIN_REQUIREMENTS) -and ($adrs.Count -ge $MIN_ADRS) -and ($adrOk -eq $adrs.Count) -and ($plans.Count -ge $MIN_PLANS) -and ($duplicates.Count -eq 0)) "features $($ftrs.Count), requirements $rqCount, ADRs $($adrs.Count) ($adrOk with DEC and diagram), plans $($plans.Count), duplicate IDs $($duplicates.Count)"

# RQ-DMO-006
$earsOk = @('Ubiquitous', 'Event-driven', 'State-driven', 'Unwanted-behavior') | Where-Object { $allProcessText -notmatch ('\*\*EARS Type\*\*: ' + $_) }
$tiersPresent = @('S', 'M', 'L' | Where-Object { $tier = $_; @($planTasks | Where-Object { $_.Tier -eq $tier }).Count -gt 0 })
$unfilled = @($planTasks | Where-Object { $_.Tier -in 'M', 'L' -and ($_.Verification -match '^(Pending|Filled)' -or -not $_.Verification -or -not $_.Assumptions) })
$alternatives = @($adrs | Where-Object { ((Demo-Git @('show', "HEAD:$_")) -join "`n") -match '## Alternatives Considered' }).Count
$logText = if ($demoFiles -contains "$AGNOS_FOLDER/$AGNOS_METRICS_LOG") { (Demo-Git @('show', "HEAD:$AGNOS_FOLDER/$AGNOS_METRICS_LOG")) -join "`n" } else { '' }
$logRows = ([regex]::Matches($logText, '(?m)^\| \d{4}-\d{2}-\d{2} \|')).Count
$sessionBranches = @(Demo-Git @('branch', '--list', 'feature/*'))
Report 'RQ-DMO-006' (($earsOk.Count -eq 0) -and ($tiersPresent.Count -eq 3) -and ($unfilled.Count -eq 0) -and ($alternatives -eq $adrs.Count) -and ($logRows -ge $sessionBranches.Count)) "missing EARS types: $($earsOk.Count); tiers present: $($tiersPresent -join ''); M/L tasks unfilled: $($unfilled.Count); metrics rows $logRows for $($sessionBranches.Count) sessions"

# RQ-DMO-007
$indexRun = Start-Process -FilePath powershell -ArgumentList '-NoProfile', '-File', (Join-Path $Toolkit $INDEX_SCRIPT) -WorkingDirectory $Demo -Wait -PassThru -WindowStyle Hidden
$dirty = @(Demo-Git @('status', '--porcelain'))
Report 'RQ-DMO-007' (($indexRun.ExitCode -eq 0) -and ($dirty.Count -eq 0)) "agnos-index exit $($indexRun.ExitCode); working tree changes after the run: $($dirty.Count)"

# RQ-DMO-008
$traceDir = Join-Path ([System.IO.Path]::GetTempPath()) ($REBUILD_FOLDER_PREFIX + 'trace-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $traceDir | Out-Null
$traceScript = Join-Path $Toolkit '.github/skills/agnos-perf-center/scripts/perf_center.py'
# RQ-TRC-132 (TASK-TRC-122): --rebuild runs agnos-graph, which writes the state in the knowledge folder; removed after, the demo stays clean
$traceGraph = Join-Path (Join-Path $Demo $AGNOS_FOLDER) $AGNOS_GRAPH_FILE
$traceOut = (& python $traceScript --process (Join-Path $Demo $AGNOS_FOLDER) --sources (Join-Path $Demo 'service') --sources (Join-Path $Demo 'client') --out (Join-Path $traceDir 'trace.html') --rebuild | Out-String)
$traceExit = $LASTEXITCODE
$graphWritten = Test-Path -LiteralPath $traceGraph -PathType Leaf
if ($graphWritten) { Remove-Item -LiteralPath $traceGraph -Force }
Remove-Item -LiteralPath $traceDir -Recurse -Force
# The generator's summary line since its quality scorecard (FTR-TRC-003): "RQ n: covered n, indirect n, uncovered n;
# quality: <grade> <score>/10; checks: covered s, defined s, tasked s, task-rq s, ..."
$gaps = [regex]::Match($traceOut, 'uncovered (\d+); quality: .*?checks: covered [\d.na/]+, defined ([\d.na/]+), tasked [\d.na/]+, task-rq ([\d.na/]+)')
$traceOk = ($traceExit -eq 0) -and $graphWritten -and $gaps.Success -and ($gaps.Groups[1].Value -eq '0') -and ($gaps.Groups[2].Value -eq $FULL_SCORE) -and ($gaps.Groups[3].Value -in $FULL_SCORE, $NO_SCORE)
Report 'RQ-DMO-008' $traceOk ("agnos-perf-center: " + $(if ($gaps.Success) { "uncovered $($gaps.Groups[1].Value), IDs defined score $($gaps.Groups[2].Value), tasks with a requirement score $($gaps.Groups[3].Value)" } else { 'no summary (exit ' + $traceExit + ')' }) + "; graph $AGNOS_GRAPH_FILE written: $graphWritten")

# RQ-DMO-009
$readme = if ($demoFiles -contains 'README.md') { (Demo-Git @('show', 'HEAD:README.md')) } else { @() }
Report 'RQ-DMO-009' ((($readme | Select-Object -First 12) -join ' ') -match 'simulated' -and ($readme -join "`n") -match "git log --author=-$FILTER_ROLE") 'README opens with the simulation notice and gives the filter command'

# RQ-DMO-010
$remotes = @(Demo-Git @('remote'))
$record = Join-Path $Demo $BUILD_RECORD
$globalOk = (Test-Path -LiteralPath $record) -and ((Get-Content -LiteralPath $record -Raw | ConvertFrom-Json).globalConfigUnchanged -eq $true)
$outside = @()
if ($BaseRef) {
  $changed = @(& git -C $Toolkit diff --name-only $BaseRef) + @(& git -C $Toolkit ls-files --others --exclude-standard)
  $outside = @($changed | Where-Object { $_ -and $_ -notmatch "^$PF/|^\.github/skills/$SKILL_NAME/|^\.claude/skills/$SKILL_NAME/" })
}
Report 'RQ-DMO-010' (($remotes.Count -eq 0) -and $globalOk -and ($outside.Count -eq 0)) "remotes: $($remotes.Count); global git configuration unchanged by the build: $globalOk; toolkit files changed outside DMO and the skill: $($outside.Count)"

# RQ-DMO-011
$names = @($humanCommits | ForEach-Object { $_.AuthorName; $_.CommitterName } | Sort-Object -Unique)    # amended: agents exempt
$badNames = @($names | Where-Object { $_ -notmatch $ROLE_PATTERN })
$badMails = @($humanCommits | Where-Object { $_.AuthorEmail -ne ($_.AuthorName + $HUMAN_MAIL_DOMAIN) } | ForEach-Object { $_.AuthorEmail } | Sort-Object -Unique)
$byRole = $names | Where-Object { $_ -match $ROLE_PATTERN } | Group-Object { $_ -replace '^[a-z]+-', '' }
$roleCount = @{}; foreach ($g in $byRole) { $roleCount[$g.Name] = $g.Count }
$wrongRoles = @($EXPECTED_ROLES.Keys | Where-Object { [int]$roleCount[$_] -ne $EXPECTED_ROLES[$_] } | ForEach-Object { "$_=$([int]$roleCount[$_]) (expected $($EXPECTED_ROLES[$_]))" })
$expectedCount = ($EXPECTED_ROLES.Values | Measure-Object -Sum).Sum
$roleLog = @(Demo-Git @('log', '--all', "--author=-$FILTER_ROLE", '--format=%an') | Sort-Object -Unique)
$roleLogOk = ($roleLog.Count -gt 0) -and (@($roleLog | Where-Object { $_ -notmatch "-$FILTER_ROLE`$" }).Count -eq 0)
Report 'RQ-DMO-011' (($names.Count -eq $expectedCount) -and ($badNames.Count -eq 0) -and ($badMails.Count -eq 0) -and ($wrongRoles.Count -eq 0) -and $roleLogOk) "human identities $($names.Count) of $expectedCount ($(($names) -join ', ')); badly named: $($badNames.Count); e-mails not $HUMAN_MAIL_DOMAIN`: $($badMails.Count); roles off: $(if ($wrongRoles.Count) { $wrongRoles -join ', ' } else { 'none' }); --author=-$FILTER_ROLE returns only $FILTER_ROLE`: $roleLogOk"

# RQ-DMO-012
$firstAuthor = @{}
$current = $null
foreach ($line in (Demo-Git @('log', '--all', '--reverse', '--topo-order', '--diff-filter=A', '--name-only', '--format=@%an'))) {
  if ($line.StartsWith('@')) { $current = $line.Substring(1) } elseif ($line -and -not $firstAuthor.ContainsKey($line)) { $firstAuthor[$line] = $current }
}
$roleProblems = New-Object System.Collections.ArrayList
foreach ($file in $firstAuthor.Keys) {
  foreach ($rule in $ROLE_BY_PATH) {
    if ($file -match $rule.Pattern -and $file -notmatch '__init__\.py$' -and $firstAuthor[$file] -notmatch ('-' + $rule.Role + '$')) { [void]$roleProblems.Add("$file by $($firstAuthor[$file]), expected $($rule.Role)") }
  }
}
$order = @{}; for ($i = 0; $i -lt $plainCommits.Count; $i++) { $order[$plainCommits[$i].Hash] = $i }
foreach ($task in ($planTasks | Where-Object { $_.Tier -in 'M', 'L' })) {
  $mine = @($plainCommits | Where-Object { $_.Subject -match [regex]::Escape($task.Id) })
  $tests = @($mine | Where-Object { $_.Subject -match '^test\(' }); $code = @($mine | Where-Object { $_.Subject -notmatch '^test\(' })
  if (-not $tests.Count -or -not $code.Count -or $order[$tests[0].Hash] -ge $order[$code[0].Hash]) { [void]$roleProblems.Add("$($task.Id) tests do not precede its code") }
}
Report 'RQ-DMO-012' ($roleProblems.Count -eq 0) $(if ($roleProblems.Count) { Show-Failures $roleProblems } else { 'artifacts first committed by their role; tests precede code for every M/L task' })

# RQ-DMO-013
$dateProblems = @($commits | Where-Object { $_.AuthorDate -ne $_.CommitterDate -or $_.AuthorName -ne $_.CommitterName -or $_.AuthorEmail -ne $_.CommitterEmail })
Report 'RQ-DMO-013' ($dateProblems.Count -eq 0) "commits where author and committer differ: $($dateProblems.Count) of $($commits.Count)"

# RQ-DMO-014
$span = ($commits[-1].Day - $commits[0].Day).Days
# RQ-DMO-014 as amended: the agents are exempt from the activity rule
$activity = $humanCommits | Group-Object AuthorName | ForEach-Object { [pscustomobject]@{ Name = $_.Name; Days = @($_.Group | ForEach-Object { $_.Day.ToString('yyyy-MM-dd') } | Sort-Object -Unique).Count } }
$flat = @($activity | Where-Object { $_.Days -lt $MIN_ACTIVE_DAYS -or $_.Days -gt ($MAX_ACTIVE_RATIO * $workingDays.Count) })
Report 'RQ-DMO-014' (($span -ge $MIN_SPAN_DAYS) -and ($span -le $MAX_SPAN_DAYS) -and ($commits.Count -ge $MIN_COMMITS) -and ($flat.Count -eq 0)) "span $span days, $($commits.Count) commits, active days: $(($activity | ForEach-Object { $_.Name + '=' + $_.Days }) -join ', ') of $($workingDays.Count) working days"

# RQ-DMO-015
$offDays = @($commits | Where-Object { $_.Day.DayOfWeek -in 'Saturday', 'Sunday' -or $holidayDates -contains $_.Day.ToString('yyyy-MM-dd') })
$weekdayHolidays = @($holidayDates | Where-Object { $d = [datetime]::ParseExact($_, 'yyyy-MM-dd', $null); $d -ge $periodStart -and $d -le $periodEnd -and $d.DayOfWeek -notin 'Saturday', 'Sunday' })
$calendar = if ($demoFiles -contains 'docs/WORKING_CALENDAR.md') { (Demo-Git @('show', 'HEAD:docs/WORKING_CALENDAR.md')) -join "`n" } else { '' }
$undeclared = @($holidayDates | Where-Object { $calendar -notmatch [regex]::Escape($_) })
Report 'RQ-DMO-015' (($offDays.Count -eq 0) -and ($weekdayHolidays.Count -ge $MIN_HOLIDAYS) -and ($undeclared.Count -eq 0)) "commits on weekends or holidays: $($offDays.Count); declared weekday holidays: $($weekdayHolidays.Count); missing from the calendar file: $($undeclared.Count)"

# RQ-DMO-016
$outOfHours = @($commits | Where-Object { $_.Time -lt $plan.period.workFrom -or $_.Time -gt $plan.period.workTo })
$offsets = @($commits | ForEach-Object { $_.Offset } | Sort-Object -Unique)
Report 'RQ-DMO-016' (($outOfHours.Count -eq 0) -and ($offsets.Count -eq 1)) "commits outside $($plan.period.workFrom)-$($plan.period.workTo): $($outOfHours.Count); UTC offsets: $($offsets -join ', ')"

# RQ-DMO-017
$known = @{}
$orderProblems = New-Object System.Collections.ArrayList
$logPatch = Demo-Git @('log', '--all', '--reverse', '--topo-order', '--no-merges', '-p', '-U0', '--no-color', '--format=@@@%H%x1f%s', '--', $AGNOS_FOLDER, 'service', 'client', ":!$AGNOS_FOLDER/$AGNOS_INDEX")
$blocks = @(); $header = $null; $added = New-Object System.Collections.ArrayList
foreach ($line in $logPatch) {
  if ($line.StartsWith('@@@')) { if ($header) { $blocks += , @($header, @($added)) }; $header = $line.Substring(3); [void]($added = New-Object System.Collections.ArrayList) }
  elseif ($line.StartsWith('+') -and -not $line.StartsWith('+++')) { [void]$added.Add($line) }
}
if ($header) { $blocks += , @($header, @($added)) }
foreach ($block in $blocks) {
  $subject = ($block[0] -split $FIELD_SEPARATOR)[1]
  foreach ($line in $block[1]) { $m = [regex]::Match($line, $DEFINITION_PATTERN); if ($m.Success) { $known[$m.Groups[1].Value] = $true } }
  $cited = @(([regex]::Matches((@($subject) + $block[1]) -join "`n", $ID_PATTERN)) | ForEach-Object { $_.Value } | Sort-Object -Unique)
  foreach ($id in $cited) { if (-not $known.ContainsKey($id)) { [void]$orderProblems.Add("$id cited before its definition in '$subject'") } }
}
Report 'RQ-DMO-017' ($orderProblems.Count -eq 0) $(if ($orderProblems.Count) { Show-Failures $orderProblems } else { "$($blocks.Count) commits checked, 0 citation before definition" })

# RQ-DMO-018
$badMessages = @($commits | Where-Object { $_.Subject -match 'TASK-' -and $_.Parents.Count -le 1 -and $_.Subject -notmatch $TASK_COMMIT_PATTERN })
$merges = @($commits | Where-Object { $_.Parents.Count -gt 1 -and $_.Subject -match "^Merge branch 'feature/[A-Z]{3}'" })
Report 'RQ-DMO-018' (($badMessages.Count -eq 0) -and ($merges.Count -ge $MIN_SESSIONS) -and ($sessionBranches.Count -ge $MIN_SESSIONS)) "task messages not matching the skill format: $($badMessages.Count); session branches merged: $($merges.Count)"

# RQ-DMO-019
$fsckOk = Demo-Git-Ok @('fsck', '--strict')
$future = @($commits | Where-Object { $_.Day -gt (Get-Date).Date })
$epochByHash = @{}; foreach ($c in $commits) { $epochByHash[$c.Hash] = $c.Epoch }
$olderThanParent = @($commits | Where-Object { $c = $_; @($c.Parents | Where-Object { $epochByHash[$_] -gt $c.Epoch }).Count -gt 0 })
Report 'RQ-DMO-019' ($fsckOk -and ($future.Count -eq 0) -and ($olderThanParent.Count -eq 0)) "git fsck --strict ok: $fsckOk; commits in the future: $($future.Count); commits older than a parent: $($olderThanParent.Count)"

# RQ-DMO-023 to RQ-DMO-026: one run of the Performance Center with the history and the call graph
$historyDir = Join-Path ([System.IO.Path]::GetTempPath()) ($REBUILD_FOLDER_PREFIX + 'history-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $historyDir | Out-Null
$historyOut = (& python $traceScript --process (Join-Path $Demo $AGNOS_FOLDER) --sources (Join-Path $Demo 'service') --sources (Join-Path $Demo 'client') --history --call-graph --out (Join-Path $historyDir 'trace.html') --rebuild | Out-String)
# RQ-TRC-132 (TASK-TRC-122): the graph is rebuilt with the history, then removed so the demo stays clean
if (Test-Path -LiteralPath $traceGraph -PathType Leaf) { Remove-Item -LiteralPath $traceGraph -Force }
$historyJson = Join-Path $historyDir 'trace.json'
$historyData = if (Test-Path -LiteralPath $historyJson) { [System.IO.File]::ReadAllText($historyJson) | ConvertFrom-Json } else { $null }
Remove-Item -LiteralPath $historyDir -Recurse -Force

# RQ-DMO-023: the four kinds of commits and their proportions
$agentOnly = @($plainCommits | Where-Object { $agentNames -contains $_.AuthorName })
$together = @($plainCommits | Where-Object { $_.CoAuthors.Count -gt 0 })
$humanAlone = @($plainCommits | Where-Object { $agentNames -notcontains $_.AuthorName -and $_.CoAuthors.Count -eq 0 })
$coAuthorNames = @($together | ForEach-Object { $_.CoAuthors } | ForEach-Object { ($_ -replace ' <[^>]*>$', '') })
$claudeCount = @($coAuthorNames | Where-Object { $_.StartsWith($CLAUDE_HARNESS) }).Count
$copilotCount = @($coAuthorNames | Where-Object { $_.StartsWith($COPILOT_HARNESS) }).Count
$opusCount = @($coAuthorNames | Where-Object { $_ -eq $CLAUDE_OPUS }).Count
$sonnetCount = @($coAuthorNames | Where-Object { $_ -eq $CLAUDE_SONNET }).Count
$haikuCount = @($coAuthorNames | Where-Object { $_ -eq $CLAUDE_HAIKU }).Count
$mergesWithCoAuthor = @($commits | Where-Object { $_.Parents.Count -gt 1 -and ($_.CoAuthors.Count -gt 0 -or $agentNames -contains $_.AuthorName) })
$plainTotal = [math]::Max(1, $plainCommits.Count)
$togetherRatio = $together.Count / $plainTotal; $humanRatio = $humanAlone.Count / $plainTotal
$summary = [regex]::Match($historyOut, $HISTORY_SUMMARY_PATTERN)
$agentsSeen = if ($summary.Success) { [int]$summary.Groups[3].Value } else { -1 }
# RQ-DMO-023 as amended on 2026-11-12: each human makes most of its own non-merge commits with an agent
$personShares = @($plainCommits | Where-Object { $agentNames -notcontains $_.AuthorName } | Group-Object AuthorName | ForEach-Object {
  [pscustomobject]@{ Name = $_.Name; Ratio = @($_.Group | Where-Object { $_.CoAuthors.Count -gt 0 }).Count / $_.Count } })
$lowShares = @($personShares | Where-Object { $_.Ratio -lt $MIN_PERSON_AGENT_RATIO })
$sharesText = ($personShares | ForEach-Object { '{0} {1:P0}' -f $_.Name, $_.Ratio }) -join ', '
Report 'RQ-DMO-023' (($lowShares.Count -eq 0) -and ($togetherRatio -ge $MIN_TOGETHER_RATIO) -and ($togetherRatio -le $MAX_TOGETHER_RATIO) -and ($humanRatio -ge $MIN_HUMAN_RATIO) -and ($claudeCount -ge $MIN_HARNESS_COMMITS) -and ($copilotCount -ge $MIN_HARNESS_COMMITS) -and ($opusCount -ge $MIN_MAIN_MODEL_COMMITS) -and ($sonnetCount -ge $MIN_MAIN_MODEL_COMMITS) -and ($haikuCount -ge $MIN_HAIKU_COMMITS) -and ($haikuCount -le $MAX_HAIKU_COMMITS) -and ($agentOnly.Count -ge $MIN_AGENT_ONLY) -and ($agentOnly.Count -le $MAX_AGENT_ONLY) -and ($mergesWithCoAuthor.Count -eq 0) -and ($agentsSeen -eq $EXPECTED_AGENTS)) ("of {0} non-merge commits: together {1} ({2:P0}), human alone {3} ({4:P0}), agent alone {5}; Claude Code {6} (Opus {7}, Sonnet {8}, Haiku {9}), Copilot {10}; merges with an agent: {11}; agents counted by agnos-perf-center: {12}; with an agent per human: {13}" -f $plainCommits.Count, $together.Count, $togetherRatio, $humanAlone.Count, $humanRatio, $agentOnly.Count, $claudeCount, $opusCount, $sonnetCount, $haikuCount, $copilotCount, $mergesWithCoAuthor.Count, $agentsSeen, $sharesText)

# RQ-DMO-024: one trailer at most, one of the scenario's agents
$manyTrailers = @($commits | Where-Object { $_.CoAuthors.Count -gt 1 })
$unknownTrailers = @($commits | ForEach-Object { $_.CoAuthors } | Where-Object { $agentTrailers -notcontains $_ } | Sort-Object -Unique)
Report 'RQ-DMO-024' (($manyTrailers.Count -eq 0) -and ($unknownTrailers.Count -eq 0)) "commits with more than one trailer: $($manyTrailers.Count); trailers not of a scenario agent: $(if ($unknownTrailers.Count) { $unknownTrailers -join ', ' } else { 'none' })"

# RQ-DMO-025: an agent alone is its own committer, holds no trailer, has one parent and adds no file
$agentProblems = New-Object System.Collections.ArrayList
foreach ($c in @($commits | Where-Object { $agentNames -contains $_.AuthorName })) {
  if ($c.CommitterName -ne $c.AuthorName -or $c.CommitterEmail -ne $c.AuthorEmail) { [void]$agentProblems.Add("$($c.Subject): committer differs") }
  if ($c.CoAuthors.Count -gt 0) { [void]$agentProblems.Add("$($c.Subject): holds a trailer") }
  if ($c.Parents.Count -ne 1) { [void]$agentProblems.Add("$($c.Subject): $($c.Parents.Count) parents") }
  $addedFiles = @(Demo-Git @('diff-tree', '--no-commit-id', '-r', '--diff-filter=A', '--name-only', $c.Hash) | Where-Object { $_ })
  if ($addedFiles.Count) { [void]$agentProblems.Add("$($c.Subject): adds $($addedFiles -join ', ')") }
}
$mergedAgents = @($historyData.history.people | Where-Object { $_.kind -eq $AGENT_KIND -and $_.commits -gt 0 -and $_.coCommits -gt 0 })
$aloneAuthors = @($agentOnly | ForEach-Object { $_.AuthorName } | Sort-Object -Unique)
Report 'RQ-DMO-025' (($agentProblems.Count -eq 0) -and ($mergedAgents.Count -ge $aloneAuthors.Count)) $(if ($agentProblems.Count) { Show-Failures $agentProblems } else { "$($agentOnly.Count) agent-only commits, each its own committer, without trailer, one parent, no file added; agents both author and co-author, merged into one identity: $($mergedAgents.Count)" })

# RQ-DMO-026: the "Functions traced" check of the Performance Center
$functionCheck = @($historyData.quality.checks | Where-Object { $_.key -eq $FUNCTION_CHECK }) | Select-Object -First 1
$functionScore = if ($functionCheck) { [double]$functionCheck.score } else { -1 }
$uncitedCount = if ($functionCheck) { @($functionCheck.findings).Count } else { -1 }
Report 'RQ-DMO-026' (($functionScore -ge $MIN_FUNCTION_SCORE) -and ($functionScore -lt $MAX_FUNCTION_SCORE)) $(if ($functionCheck) { "Functions traced $functionScore ($uncitedCount uncited of $($functionCheck.population))" } else { 'no functions-traced check (call-graph packages missing?)' })

# RQ-DMO-022: the design system and the interface made on it, the UX designer's work, the client's tests
$indexText = if (Test-Path -LiteralPath (Join-Path $Demo "$AGNOS_FOLDER/$AGNOS_INDEX")) { [System.IO.File]::ReadAllText((Join-Path $Demo "$AGNOS_FOLDER/$AGNOS_INDEX")) } else { '' }
$uiMissing = @($UI_ARTIFACTS | Where-Object { $indexText -notmatch ('(?m)^' + [regex]::Escape($_) + '\|') })
$webPlan = @(Get-ChildItem -LiteralPath (Join-Path $Demo "$AGNOS_FOLDER/3.plan") -Filter 'PLAN-WEB-*.md' -ErrorAction SilentlyContinue)
$webCitesDesign = ($webPlan.Count -gt 0) -and ([System.IO.File]::ReadAllText($webPlan[0].FullName) -match '(RQ|ADR|DEC)-DSN-\d{3}')
$uxCommits = @(Demo-Git @('log', '--all', '--author=-ux', '--format=%h'))
$clientTests = Start-Process -FilePath node -ArgumentList '--test', 'tests/*.test.ts' -WorkingDirectory (Join-Path $Demo 'client') -Wait -PassThru -WindowStyle Hidden
Report 'RQ-DMO-022' (($uiMissing.Count -eq 0) -and $webCitesDesign -and ($uxCommits.Count -gt 0) -and ($clientTests.ExitCode -eq 0)) "design system and interface artifacts missing: $(if ($uiMissing.Count) { $uiMissing -join ', ' } else { 'none' }); UI plan cites the design system: $webCitesDesign; commits by a ux identity: $($uxCommits.Count); client tests exit $($clientTests.ExitCode)"

# RQ-DMO-027: the README's commands start the service and the interface, and the interface and the tool show a room of the file
function Wait-Http([string]$Url) {
  $deadline = (Get-Date).AddSeconds($RUN_WAIT_SECONDS)
  while ((Get-Date) -lt $deadline) {
    try { $r = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec $RUN_WAIT_SECONDS; if ($r.StatusCode -eq $HTTP_OK) { return $r.Content } } catch { }
    Start-Sleep -Milliseconds $RUN_POLL_MS
  }
  return $null
}
$readmeText = $readme -join "`n"
$commandsMissing = @($SERVICE_COMMAND, $UI_COMMAND, $CLI_COMMAND | Where-Object { -not $readmeText.Contains($_) })
$roomName = $null
if (Test-Path -LiteralPath (Join-Path $Demo $ROOMS_FILE)) { $rooms = [System.IO.File]::ReadAllText((Join-Path $Demo $ROOMS_FILE)) | ConvertFrom-Json; $roomName = $rooms[0].name }
$service = $null; $ui = $null; $runProblems = New-Object System.Collections.ArrayList
try {
  $service = Start-Process -FilePath python -ArgumentList '-m', 'roombook' -WorkingDirectory (Join-Path $Demo 'service') -PassThru -WindowStyle Hidden
  $ui = Start-Process -FilePath node -ArgumentList $UI_ENTRY -WorkingDirectory (Join-Path $Demo 'client') -PassThru -WindowStyle Hidden
  if (-not $roomName) { [void]$runProblems.Add("no room in $ROOMS_FILE") }
  if ($null -eq (Wait-Http $SERVICE_ROOMS_URL)) { [void]$runProblems.Add("service does not answer $SERVICE_ROOMS_URL (exited: $($service.HasExited))") }
  else {
    $page = Wait-Http $UI_URL
    if ($null -eq $page) { [void]$runProblems.Add("interface does not answer 200 on $UI_URL") }
    elseif ($roomName -and -not $page.Contains($roomName)) { [void]$runProblems.Add("interface page lacks the room $roomName") }
    Push-Location (Join-Path $Demo 'client')
    try { $cliOut = (& node $CLI_ENTRY $CLI_ROOMS 2>&1) -join "`n"; $cliExit = $LASTEXITCODE } finally { Pop-Location }
    if ($cliExit -ne 0) { [void]$runProblems.Add("command-line tool exit $cliExit") }
    elseif ($roomName -and -not $cliOut.Contains($roomName)) { [void]$runProblems.Add("command-line tool output lacks the room $roomName") }
  }
} finally {
  foreach ($p in @($service, $ui)) { if ($p -and -not $p.HasExited) { Stop-Process -Id $p.Id -Force } }
}
Report 'RQ-DMO-027' (($commandsMissing.Count -eq 0) -and ($runProblems.Count -eq 0)) "README commands missing: $(if ($commandsMissing.Count) { $commandsMissing -join ' | ' } else { 'none' }); run: $(if ($runProblems.Count) { Show-Failures $runProblems } else { "service, interface and command-line tool show $roomName" })"

# RQ-INI-008: the two files hold the block alone, and a new agnos-init call on the demo changes nothing
$blockOnly = @($INIT_FILES | Where-Object {
  (Test-Path -LiteralPath (Join-Path $Demo $_)) -and ([System.IO.File]::ReadAllText((Join-Path $Demo $_)).TrimEnd()) -match "^$([regex]::Escape($BLOCK_BEGIN))" -and ([System.IO.File]::ReadAllText((Join-Path $Demo $_)).TrimEnd()).EndsWith($BLOCK_END)
})
$initRun = Start-Process -FilePath powershell -ArgumentList '-NoProfile', '-File', (Join-Path $Toolkit $INIT_SCRIPT), '-Target', '.' -WorkingDirectory $Demo -Wait -PassThru -WindowStyle Hidden
$initDirty = @(Demo-Git @('status', '--porcelain'))
Report 'RQ-INI-008' (($blockOnly.Count -eq $INIT_FILES.Count) -and ($initRun.ExitCode -eq 0) -and ($initDirty.Count -eq 0)) "files with the block alone: $($blockOnly.Count) of $($INIT_FILES.Count); agnos-init exit $($initRun.ExitCode); changes after the call: $($initDirty.Count)"

# RQ-DMO-020
$skillFiles = @(".github/skills/$SKILL_NAME/SKILL.md", ".claude/skills/$SKILL_NAME/SKILL.md", ".github/skills/$SKILL_NAME/scripts/replay.ps1", ".github/skills/$SKILL_NAME/scripts/verify.ps1", ".github/skills/$SKILL_NAME/scripts/build.ps1")
$absent = @($skillFiles | Where-Object { -not (Test-Path -LiteralPath (Join-Path $Toolkit $_)) })
$skillText = if (-not $absent.Count) { [System.IO.File]::ReadAllText((Join-Path $Toolkit $skillFiles[0])) } else { '' }
Report 'RQ-DMO-020' (($absent.Count -eq 0) -and ($skillText -match '(?m)^### `build') -and ($skillText -match '(?m)^### `verify')) "skill files absent: $($absent.Count); sub-commands build and verify documented"

# RQ-DMO-021
if ($SkipRebuild) { Report 'RQ-DMO-021' $true 'skipped (-SkipRebuild)' } else {
  $temp = Join-Path (Split-Path -Parent $Toolkit) ($REBUILD_FOLDER_PREFIX + [guid]::NewGuid().ToString('N'))   # beside the toolkit, as the check of the demo's place requires (RQ-DMO-001)
  $replay = Start-Process -FilePath powershell -ArgumentList '-NoProfile', '-File', (Join-Path $PSScriptRoot 'replay.ps1'), '-Scenario', $Scenario, '-Content', (Join-Path $PSScriptRoot '../assets/content'), '-Toolkit', $Toolkit, '-Target', $temp -Wait -PassThru -WindowStyle Hidden
  $same = $false
  if ($replay.ExitCode -eq 0) { $same = ((& git -C $temp rev-parse HEAD) -eq (& git -C $Demo rev-parse HEAD)) }
  if (Test-Path -LiteralPath (Join-Path $temp '.git/agnos-demo-generated')) { Remove-Item -LiteralPath $temp -Recurse -Force }
  Report 'RQ-DMO-021' $same "second build exit $($replay.ExitCode); same HEAD as the demo: $same"
}

$failed = @($results | Where-Object { -not $_.Ok })
Write-Output ('agnos-meta-demo verify: {0} passed, {1} failed' -f ($results.Count - $failed.Count), $failed.Count)
exit $(if ($failed.Count) { 1 } else { 0 })
