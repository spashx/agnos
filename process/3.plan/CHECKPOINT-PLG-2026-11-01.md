# Checkpoint: Session PLG, on 2026-11-01

Read this first when resuming, on any workstation. <!-- PLAN-PLG-001 / ADR-PLG-001, ADR-MTA-001, ADR-MTA-002, ADR-INI-001 / FTR-PLG-001 -->

## State
- **Checked on 2026-11-03**: branch, last commit, ahead count, demo HEAD and open tasks below match the repository and the index; no commit since `1361a8b`. This file itself is still uncommitted.
- **Branch**: `feature/PLG`, 181 commits ahead of `main`, created from `feature/TRC`. Last task commit: `1361a8b`. It has no upstream.
- **Standing constraint**: push nothing, CI included, until the owner lifts it. Do not propose an exception. (DEC-MTA-004, DEC-PLG-007)
- **Session variables**: `unit_tests: true`, `platform: windows`. Resolve them again if the workstation's system differs.
- **Session PLG is closed**: its report is given, its metrics row is in `METRICS_LOG.md`, and its self-improvement iteration 1/1 is committed. A new start needs START SESSION; the branch exists, so `start-session PLG` asks how to proceed: check it out.
- **Open tasks**: one, TASK-PLG-007. Every other indexed task is Done.
- **Demo**: `agnos-lightweight-process.demo`, beside this repository, HEAD `36f221f`, 23 checks of 23. `agnos-meta-release` needs it for its proof.

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

## Open: TASK-PLG-007, the owner's checks
Until these are done, the task stays In Progress and RQ-PLG-009 is not fulfilled. Each result updates the "What was tested" table of `README.md`, which states observed results only.

Rebuild the marketplace first: the last one was built from `f0433ef`, in a temporary folder of the former workstation, and lacks the later documents and rule.

```
python .github/skills/agnos-meta-release/scripts/release.py --dry-run --output <folder>
python .github/skills/agnos-meta-plugin-proof/scripts/plugin_proof.py --marketplace <folder>
```

| # | Check | Expected |
|---|---|---|
| 1 | Full session in Claude Code, on a new project, up to a first commit | Install, `agnos-init`, new session, START SESSION with its question, index, branch, one task, `commit-task` |
| 2 | The same in GitHub Copilot CLI | The same; notably that `validate-ids` runs once approved, which the proof never observed |
| 3 | GitHub Copilot in VS Code | Never run: install, skills found, block loaded |
| 4 | `agnos-meta-docs-sync` on Haiku in a Claude Code session | The sub-agent runs its procedure and edits the four documents only |

## Not possible yet
| Item | Why |
|---|---|
| Install from a remote repository, with its per-version folder | Needs a push, the owner's decision; `file://`, dumb http and `git://` do not stand in |
| OpenAI Codex | Not run: its CLI only adds a marketplace, the install goes through the ChatGPT desktop app |
| macOS | Only through CI, so needs a push; shares the Linux scripts |
| A tool on Linux | No Claude Code or Copilot in the WSL image; scripts and suites pass there, with the browser and tree-sitter tests skipped (237) |

## Before a real release
- Owner's decision to publish, then the checks above.
- Rerun `agnos-meta-docs-sync`: `[Unreleased]` is current up to `c5ffada`.
- `[Unreleased]` holds every change since v3.1, and no version number has been decided: the plugin takes 3.1.0 from the changelog's latest release.

## Key decisions
- DEC-PLG-001: one marketplace, one plugin, built by the release. DEC-PLG-002: the process is a generated skill. DEC-PLG-003: the block names the skill. DEC-PLG-004: skills name their files from their folder. DEC-PLG-005: agents generated from `.github/agents`; Codex receives none. DEC-PLG-006: tested on Windows and Linux, the rest stated. DEC-PLG-007: no push, install from a clean local clone.
- The copy format is abandoned; the plugin is the only way in.

## Facts from the trials
- Copilot ignores `agents/` under a root Agent Plugins manifest; agents live in `com.github.copilot/agents/`.
- `${CLAUDE_SKILL_DIR}` is empty on Copilot, hence `<skill-folder>` in the skills.
- Copilot's block fires on work questions, not on trivial ones.
- `claude` may not be on the PATH: name its binary in the variable `AGNOS_CLAUDE`.
- Never `--allow-all-tools`: only narrow grants.

## Last suite results
On `feature/PLG`, Windows: meta-release 63, meta-demo 12, plugin-proof 16 and docs-sync 16 OK, with no test skipped on those; init 17 OK. Perf-center's last full run, from TASK-PLG-003: 366 run, 3 skipped. It and the index suite were not rerun for the last two commits, which touch documents only.

## Working preferences held outside this repository
Claude Code's memory stays on the former workstation, so these are stated here:
- The owner writes in French; answer in French. Process documents stay in English.
- Use `rtk` on CLI calls, subagent prompts included.
- Builds run in a background Haiku subagent, never waited on; delegated full suites run on a scratchpad copy.
- Targeted tests while iterating, the full suite once before each commit. `agnos-meta-demo`'s suite counts: skipping it let a visible ID into `f0433ef`.
- Read the cited source before relaying a subagent's finding as fact.
- Session-specific lessons never go into the generic process instructions.
- Visual checks of a page are the owner's: no routine agent screenshots; UI tests measure the render.
- No implicit setup: a required step such as `agnos-init` is explicit and documented.
- Without a session started by the owner, free edits are expected, not a defect. The semantic conflict check covers the repository's instructions only.
- Every AGNOS skill follows the official authoring practices and skill-creator.
- Idea on hold: an `agnos-awareness` skill, a compact session-start summary and queries from the perf center's JSON.

# Verbatim of the agent's answer that produced this file

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