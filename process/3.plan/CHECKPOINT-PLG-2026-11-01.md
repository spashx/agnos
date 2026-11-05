# Checkpoint: Session PLG, on 2026-11-01

Read this first when resuming, on any workstation. <!-- PLAN-PLG-001, PLAN-PLG-002, PLAN-PLG-003, PLAN-PLG-004 / ADR-PLG-001 to ADR-PLG-004, ADR-MTA-001, ADR-MTA-002, ADR-INI-001 / FTR-PLG-001 to FTR-PLG-004 -->

Updated on 2026-11-05, in the session started on 2026-11-04 (PLAN-PLG-003 delivered, PLAN-PLG-004 begun), at its task-count checkpoint.

## State
- **Branch**: `feature/PLG`, 202 commits ahead of `main` before this file's commit. Last task commit: `73fdc61` (TASK-PLG-026). It has no upstream.
- **Standing constraint**: push nothing, CI included, branch included, until the owner lifts it. Do not propose an exception. (DEC-MTA-004, DEC-PLG-007)
- **Session variables**: `unit_tests: true`, `platform: windows`. Resolve them again if the workstation's system differs.
- **Session of 2026-11-04 is open**: ten tasks done, so this checkpoint; the owner chose to continue PLAN-PLG-004 in a new session. Its START SESSION keeps `feature/PLG`.
- **Open tasks**: TASK-PLG-027, TASK-PLG-028, TASK-PLG-029 (PLAN-PLG-004, approved by the owner on 2026-11-05), and TASK-PLG-007, the owner's checks.
- **Demo**: `agnos-lightweight-process.demo`, beside this repository, HEAD `4347a66`, rebuilt with the new block and guide. `agnos-meta-release` needs it for its proof.
- **Marketplace**: `C:\dev\repos\spashx\agnos-marketplace`, rehearsed from `25869d8`: `exit=0, 55 files, 1195 IDs removed, 2 lines to read`, both false alarms; proved by `plugin_proof.py`, 8 lines pass, with `AGNOS_CLAUDE` naming the VS Code extension's `claude.exe`. Its `COMPATIBILITY.md` lacks the VS Code row of `cc16965`: TASK-PLG-029 rehearses again.
- **Trial repositories**: `agnos-trial` (Claude Code, 2026-11-04) and `agnos-trial-copilot` (Copilot in VS Code, 2026-11-05), beside this one. The plugin was uninstalled from Claude Code; the marketplace stays registered. `C:\pp`, the proof's working folder, is the owner's to delete.

## Goal
One marketplace holding the plugin `agnos`, usable from GitHub Copilot, Claude Code and possibly OpenAI Codex. Every system is supported, Windows first. Agents are integrated. The release holds no ID of AGNOS's own development. macOS is not a priority and can only be tested through CI.

## Completed
| Task | Tier | Result |
|---|---|---|
| TASK-PLG-001 | L | Feature, ADR and plan, from a trial in both tools |
| TASK-PLG-002 | L | Delivered skills name their files from their own folder |
| TASK-PLG-003 | M | Delivered suites run on Ubuntu 24.04 under WSL |
| TASK-PLG-004 | L | The `agnos-init` block names `agnos-process`, with no path and no toolkit input; demo rebuilt |
| TASK-PLG-005 | L | `agnos-meta-release` writes the marketplace |
| TASK-PLG-006 | M | Agents generated per tool, proved on a test agent in both tools |
| TASK-PLG-008 | M | `agnos-meta-plugin-proof` runs the install proof again |
| TASK-PLG-009 | M | Self-improvement: the `Verification` field states the tests skipped and why |

PLAN-PLG-002, a deterministic release and its report page (FTR-PLG-002, ADR-PLG-002), all Done:

| Task | Tier | Result |
|---|---|---|
| TASK-PLG-010 | L | Feature, ADR and plan; RQ-MTA-012 amended by RQ-PLG-014 |
| TASK-PLG-011 | M | No bytecode from the checks; a file neither delivered nor generated fails the rehearsal |
| TASK-PLG-012 | M | Two rehearsals in two processes, two hash seeds: byte-identical trees, reports and pages |
| TASK-PLG-013 | M | Findings printed with file and line; the last line always gives `exit=` |
| TASK-PLG-014 | L | Manifests checked by script; the release calls no AI tool, `claude plugin validate` stays in the proof |
| TASK-PLG-015 | M | The page's tokens compiled from the output's perf center, a stylesheet with no raw value |
| TASK-PLG-016 | M | `<folder>.report.html`: self-contained, data embedded and escaped, drawn as text only |
| TASK-PLG-017 | M | The skill's procedure updated; the marketplace rehearsed again |

PLAN-PLG-003, the process speaks to a plugin user (FTR-PLG-003, ADR-PLG-003), all Done:

| Task | Tier | Result |
|---|---|---|
| TASK-PLG-018 | L | Feature, ADR and plan; RQ-PLG-004, RQ-DOC-001, RQ-DOC-002, RQ-INI-007 amended |
| TASK-PLG-019 | M | Self-improvement goes into the improvement target, the file the AGNOS block names; "this file" without its name |
| TASK-PLG-020 | M | The block reads `process/project-rules.md` and names it the target; init's last words in two steps |
| TASK-PLG-021 | M | `agnos-init` writes `AGNOS-GETTING-STARTED.md`, the former guide reworded for a plugin user |
| TASK-PLG-022 | L | `GETTING_STARTED.MD` leaves the root; docs-sync keeps the template as its fourth document |
| TASK-PLG-023 | M | The Claude Code session recorded; `[Unreleased]` holds PLAN-PLG-002 and PLAN-PLG-003 |
| TASK-PLG-025 | M | README a landing page with its Requirements; `COMPATIBILITY.md` delivered; repository map in `CONTRIBUTING.md` |
| TASK-PLG-024 | M | Rehearsal of `25869d8` and its proof |

PLAN-PLG-004, function traceability (FTR-PLG-004, ADR-PLG-004): TASK-PLG-026 (L) Done; next, in order:

| Task | Tier | To do |
|---|---|---|
| TASK-PLG-027 | M | `functions-traced` risk medium in `scoring.json`; `matrix.js` line ~1467 reads the risk from the data instead of "informational"; `references/rules.md`; tests expecting informational in `test_callgraph.py` (lines ~278, ~383) and `test_scorecard.py`; `scorecard.py` line ~176 already filters by risk |
| TASK-PLG-028 | M | The DoD line of RQ-PLG-025 in the instructions file (385 lines now), tested on `release.process_skill` as `test_process_text.py` does |
| TASK-PLG-029 | M | Demo rebuilt if needed, rehearsal and proof, perf center rerun on `agnos-trial-copilot`: its score must fall below 10 |

## Open: TASK-PLG-007, the owner's checks
Until these are done, the task stays In Progress and RQ-PLG-009 is not fulfilled. Each result updates `COMPATIBILITY.md`, which states observed results only. Done: Claude Code full session (2026-11-04), Copilot in VS Code full session (2026-11-05, with three departures: chosen files staged instead of `git add .`, functions citing no ID, no failing test shown first; model "Auto", unknown).

Use the marketplace above, or rehearse again, then prove it:

```
python .github/skills/agnos-meta-release/scripts/release.py --dry-run --output <folder>
python .github/skills/agnos-meta-plugin-proof/scripts/plugin_proof.py --marketplace <folder>
```

`claude` is not on this workstation's PATH: name `C:\Users\Linux\.vscode\extensions\anthropic.claude-code-<version>-win32-x64\resources\native-binary\claude.exe` in `AGNOS_CLAUDE` for the proof's `validate-*` lines.

| # | Check | Expected |
|---|---|---|
| 1 | A full session in GitHub Copilot CLI | The same as in VS Code; `validate-ids` was seen running in VS Code, not yet in the CLI |
| 2 | `agnos-meta-docs-sync` on Haiku in a session of the owner's | The sub-agent runs its procedure and edits the four documents only; seen from the agent's side on 2026-11-04 |

## Not possible yet
| Item | Why |
|---|---|
| Install from a remote repository, with its per-version folder | Needs a push, the owner's decision; `file://`, dumb http and `git://` do not stand in |
| OpenAI Codex | Not run: its CLI only adds a marketplace, the install goes through the ChatGPT desktop app |
| macOS | Only through CI, so needs a push; shares the Linux scripts |
| A tool on Linux | No Claude Code or Copilot in the WSL image; scripts and suites pass there, with the browser and tree-sitter tests skipped (237) |

## Before a real release
- Owner's decision to publish, then the checks above.
- Rerun `agnos-meta-docs-sync` after PLAN-PLG-004: `[Unreleased]` is current up to TASK-PLG-022.
- The page's rendering was checked by the owner on 2026-11-04.
- The two lines to read are false alarms, as on 2026-11-03; the mentions are in `CHANGELOG.md` and the perf center's `maintaining.md`.
- `[Unreleased]` holds every change since v3.1, and no version number has been decided: the plugin takes 3.1.0 from the changelog's latest release.

## Key decisions
- DEC-PLG-001: one marketplace, one plugin, built by the release. DEC-PLG-002: the process is a generated skill. DEC-PLG-003: the block names the skill. DEC-PLG-004: skills name their files from their folder. DEC-PLG-005: agents generated from `.github/agents`; Codex receives none. DEC-PLG-006: tested on Windows and Linux, the rest stated. DEC-PLG-007: no push, install from a clean local clone.
- DEC-PLG-013: the AGNOS block names `process/project-rules.md` as the improvement target. DEC-PLG-016, DEC-PLG-017: the user's guide is `agnos-init`'s template. DEC-PLG-018: one reader per document (README, `COMPATIBILITY.md`, guide, `CONTRIBUTING.md`). DEC-PLG-019, DEC-PLG-020: functions traced weighs medium; the DoD names functions.
- Owner's decisions of 2026-11-04 left as they are: `commit-task` keeps `git add .`; the project's `.gitignore` is the user's; commits outside a task (metrics log, init output) need no procedure.
- The copy format is abandoned; the plugin is the only way in.

## Facts from the trials
- Copilot ignores `agents/` under a root Agent Plugins manifest; agents live in `com.github.copilot/agents/`.
- `${CLAUDE_SKILL_DIR}` is empty on Copilot, hence `<skill-folder>` in the skills.
- Copilot's block fires on work questions, not on trivial ones.
- `claude` may not be on the PATH: name its binary in the variable `AGNOS_CLAUDE`.
- Never `--allow-all-tools`: only narrow grants.
- Copilot reads a local marketplace's plugin in place: regenerating `agnos-marketplace` changes the installed plugin, removing it breaks it.
- Copilot in VS Code sees a plugin installed from Copilot CLI: they share the configuration.
- The perf center reads a function's IDs in its lines, docstring included, and in the comment block just above it.

## Last suite results
On `feature/PLG`, Windows, 2026-11-04 and 05: meta-release 101, init 25, docs-sync 18, meta-demo 12 OK, none skipped; demo verify 23 passed. Earlier: plugin-proof 16 OK. Perf-center's last full run, from TASK-PLG-003: 366 run, 3 skipped; PLAN-PLG-002 did not touch it, and its tokens are compiled by the release's tests.

## Working preferences held outside this repository
Claude Code's memory stays on the former workstation, so these are stated here:
- The owner writes in French; answer in French. Process documents stay in English.
- Use `rtk` on CLI calls, subagent prompts included.
- Builds run in a background Haiku subagent, never waited on; delegated full suites run on a scratchpad copy.
- In these sessions, each `commit-task` runs in a Sonnet subagent at medium effort, PowerShell only, exit codes from `$LASTEXITCODE`.
- Targeted tests while iterating, the full suite once before each commit. `agnos-meta-demo`'s suite counts: skipping it let a visible ID into `f0433ef`.
- Read the cited source before relaying a subagent's finding as fact.
- Session-specific lessons never go into the generic process instructions.
- Visual checks of a page are the owner's: no routine agent screenshots; UI tests measure the render.
- No implicit setup: a required step such as `agnos-init` is explicit and documented.
- Without a session started by the owner, free edits are expected, not a defect. The semantic conflict check covers the repository's instructions only.
- Every AGNOS skill follows the official authoring practices and skill-creator.
- Idea on hold: an `agnos-awareness` skill, a compact session-start summary and queries from the perf center's JSON.

# Verbatim of the agent's answer that produced this file, on 2026-11-01 (its state is superseded by the sections above)

"Le checkpoint est écrit dans [CHECKPOINT-PLG-2026-11-01.md](process/3.plan/CHECKPOINT-PLG-2026-11-01.md), mais **il n'est pas encore commité**. Il reprend aussi mes consignes de travail, car ma mémoire reste sur ce poste.

## État du projet
- **Branche :** `feature/PLG`, à `1361a8b`, 181 commits d'avance sur `main`, jamais poussée.
- **Marketplace :** elle se construit et s'installe vraiment sur Windows, dans Claude Code et Copilot CLI (6 skills sur 6, `agnos-init`, `agnos-index`, process chargé, agent de test). Les scripts passent sur Linux.
- **Tâches ouvertes :** une seule, TASK-PLG-007. Toutes les autres tâches indexées sont terminées, et RQ-PLG-009 reste non satisfaite tant qu'elle est ouverte.

## Ce que tu dois vérifier
Commence par reconstruire la marketplace : celle de test date de `f0433ef` et n'a ni les derniers documents ni la nouvelle règle.

1. **Claude Code :** une session complète sur un projet neuf, de l'installation jusqu'au premier `commit-task`.
2. **Copilot CLI :** la même session. Regarde surtout si `validate-ids` s'exécute une fois approuvé, car la preuve ne l'a jamais observé.
3. **Copilot dans VS Code :** jamais lancé. Il faut vérifier l'installation, les skills trouvés et le bloc chargé.
4. **`agnos-meta-docs-sync` sur Haiku :** dans une session Claude Code, le sous-agent ne doit modifier que ses quatre documents.

Chaque résultat met à jour le tableau « What was tested » du README.

## Bloqué pour l'instant

| Point | Raison |
|---|---|
| Installation depuis un dépôt distant | Demande un push, donc ta décision |
| macOS | Testable seulement en CI, donc demande aussi un push |
| OpenAI Codex | Jamais lancé : son CLI ajoute seulement la marketplace, l'installation passe par l'application de bureau ChatGPT |
| Un outil sur Linux | Claude Code et Copilot ne sont pas installés dans WSL |

Avant une vraie publication, il faudra aussi décider du numéro de version (le plugin prend 3.1.0 du changelog) et relancer `agnos-meta-docs-sync`.

## Reprendre sur l'autre poste
Sans push, la branche et le dépôt de démo, dont `agnos-meta-release` a besoin, passent par un fichier `git bundle`. Il faut d'abord commiter le checkpoint : dis-moi « commit » et je le fais sous TASK-PLG-007.

**Sur ce poste :**
```
git bundle create agnos.bundle --all
git -C ..\agnos-lightweight-process.demo bundle create ..\agnos-demo.bundle --all
```

**Sur le nouveau poste,** les deux dossiers côte à côte :
```
git clone agnos.bundle agnos-lightweight-process
git clone agnos-demo.bundle agnos-lightweight-process.demo
cd agnos-lightweight-process
git checkout feature/PLG
```

Dans le dépôt cloné, `origin` pointe alors vers le fichier bundle, et non plus vers GitHub. Demande-moi ensuite de lire le checkpoint pour reprendre.
"