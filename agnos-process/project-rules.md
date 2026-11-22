# AGNOS repository rules

<!-- RQ-PLG-018, RQ-RSI-001 / TASK-RSI-007 -->
Rules of this repository, read after the process file. Each cites the friction that motivated it.

## Moving code between skills
- WHEN a task moves a script, an asset, a test or a public name from one skill to another, the agent SHALL,
  before running any suite, search the whole repository (`git grep`) for every moved path, module and name,
  and update each hit: tests reading a file by its path, other skills' runners, release, demo and website
  scripts, entry points. Motivated by METRICS_LOG 2026-11-22 TRC: ErrorRecovery 5, four of them stale references.

## Plan split
- WHEN a plan is written, the agent SHALL check that no task's acceptance criterion needs a deliverable of a
  later task, and SHALL list the existing requirements the feature hands to another component, amended in the
  first task that changes them. Motivated by METRICS_LOG 2026-11-22 TRC: AskUserQuestion 2, VerificationCatches 2.
