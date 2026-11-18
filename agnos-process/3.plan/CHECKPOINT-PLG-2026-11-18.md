# Checkpoint PLG — 2026-11-18 <!-- PLAN-PLG-013, PLAN-WEB-012; ADR-PLG-005, ADR-WEB-001 -->

## Completed
- On `feature/PLG`, local only, no push: TASK-PLG-081 `2df7e67` (demo rebuilt, verify 27 PASS, demo HEAD `279770e`), TASK-PLG-007
  `5dc2cd5` (closed by the owner), TASK-PLG-086 `d6dfcf7` (checkpoint of 2026-11-06 removed), TASK-PLG-082 `15ad02f`,
  TASK-PLG-087 `d32a795` (AGENTS.md names `dev`), TASK-WEB-025 `66568cc`, TASK-WEB-026 `55b92e8`, TASK-WEB-027 `19017d8`.
- `agnos-website`, committed locally: `fc91573 4.0.0`, then `61e02e9 4.0.0: marketplace links` (marketplace buttons, install command
  with the address, footer link to `#getting-started`, addresses in `assets/site.json` of `agnos-meta-website`).
- `agnos-meta-website` suite: 80 tests OK.
- PLAN-DOC-003 done: TASK-DOC-006 `cf1a89f` (`assets/links.json`, links test, website reads it, marketplace manifest names
  `github.com/spashx/agnos`), TASK-DOC-007 `66bb115` (README, guide row 8), TASK-DOC-009 `7926774` (release tests, COMPATIBILITY.md
  matrix), TASK-DOC-008 `fc34dcc` (demo READMEs; demo rebuilt, verify 27 PASS, HEAD `f2943d0`, imported into `../agnos-demo`, not pushed).

## Key decisions
- DEC-WEB-008 (owner, 2026-11-18): link addresses declared once in `assets/site.json`; RQ-WEB-020 added, RQ-WEB-004 and RQ-WEB-009 amended.
- Labels "AGNOS marketplace"; the header's button ghost, the install step's primary.
- The instructions keep `main` / `master` / the repository default: generic; `dev` is the default branch of this repository only.
- The plugin proof runs without `--with-models` nor `--linux`: the owner validated 3.6.2 on Linux.
- Commits in `agnos-website` and `agnos-marketplace` are made locally by the agent; merge, tag and push stay with the owner.
- DEC-DOC-001 (owner, 2026-11-18): AGNOS addresses declared once in `assets/links.json`, written as checked Markdown reference
  definitions; the README's CLI commands use the shorthand `spashx/agnos-marketplace` (not yet proved by an install).
- The demo is built as usual, then imported into `../agnos-demo` (`main` reset to the build, `origin` kept); its push, forced,
  stays with the owner; the GitHub `Initial commit` (LICENSE) is no longer in local `main`.

## Open
- The website was not rebuilt after TASK-DOC-006 (its links now come from `assets/links.json`, same addresses): rebuild it with the
  release.
- TASK-PLG-083 In Progress: `check` passed; docs-sync wrote `## [Unreleased]` in `CHANGELOG.md`, left uncommitted in the working tree.
  Next: rerun `release_prep.py review`, ask the owner to approve the diff and the version (the owner announced 4.0.0; the script
  proposed 3.7.0), `set-version`, run the release-prep suite, commit with `commit-task`.
- TASK-PLG-084 Not Started: `agnos-meta-release --dry-run` from the version commit into an empty folder outside the repository, then
  `agnos-meta-plugin-proof --marketplace <folder>`.
- TASK-PLG-085 Not Started: replace `../agnos-marketplace` (`.git` excepted) by the proved output, commit it there as `4.0.0`.

## Friction counters so far (for END SESSION)
- AskUserQuestion: 5; Error Recovery Protocol: 0; tasks re-tiered: 1 (COMPATIBILITY.md matrix, proposed M, set S by the owner);
  Verification-caught discrepancies: 2 (a page test failing since the owner's wording of 2026-11-14, found by TASK-WEB-026's run;
  the release test of COMPATIBILITY.md broken by its new matrix, found by TASK-DOC-006's run).

## Blockers
- None.
