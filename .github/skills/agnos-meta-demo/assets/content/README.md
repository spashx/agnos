# Roombook, an AGNOS demonstration

> **This history is simulated.** The people, their commits, the dates, the public holidays, the
> Verification outputs written in the plans and the friction metrics are made up to show how the AGNOS
> process looks when a team has used it for two months. Nothing here was really done by these people.

This repository holds the development of a small product, **Roombook**, following the process. AGNOS itself
is not stored here: a project is meant to receive it as a plugin, not available yet. Read this repository to see what
the process produces, or run the AGNOS skills against it to test them.

## The product

A meeting-room booking service in Python (`service/`) with a TypeScript HTTP client and command-line tool
(`client/`). It has no graphical interface, so it has no design system.

| Session | Feature | What it delivers |
|---|---|---|
| BKG | FTR-BKG-001, FTR-BKG-002 | Rooms, reservations, overlap/capacity/closed-room rules, cancellation, durable storage |
| NTF | FTR-NTF-001 | Creation event, reminders before the meeting, retries on failure |
| CLI | FTR-CLI-001 | HTTP/JSON API, typed client, command-line tool |

The process artifacts are in `process/` (requirements, ADRs, plans, session state, generated index). The code
cites them in comments, and the AGNOS traceability skill can show the links.

## The team

The role is the suffix of the identity, so the history can be filtered by role.

| Role | Suffix | Identities | Authors of |
|---|---|---|---|
| Product owner | `-po` | linda-po | features and requirements |
| Architect | `-arch` | omar-arch | ADRs, the project's start |
| Developer | `-dev` | nina-dev, paul-dev | plans, production code, session closing |
| Tester / QA | `-qa` | john-qa, sara-qa | unit tests, written before the code they check |

## Timeline

Monday 2026-08-24 to Friday 2026-10-23, Europe/Paris, working days only, 09:00 to 18:00. Two fictitious public
holidays are declared in [docs/WORKING_CALENDAR.md](docs/WORKING_CALENDAR.md). Each session is developed on a
`feature/<TRI>` branch merged into `main`: BKG 08-24 to 09-18, NTF 09-21 to 10-02, CLI 10-05 to 10-23.

## Explore

```
git log --author=-qa --format="%h %ad %an %s" --date=short     # everything done by testers
git log --author=-po --format="%h %ad %an %s" --date=short     # everything done by product owners
git log --grep=TASK-BKG-007 --format="%h %an %s"               # the commits of one task
git log --graph --oneline --all                                 # the sessions and their merges
```

## Run the tools

```
cd service && python -m unittest discover -s tests -t .         # Python tests (standard library only)
cd client && node --test "tests/*.test.ts"                      # TypeScript tests (Node 22.18 or later)
```

The AGNOS skills `agnos-index` and `agnos-trace` run from an AGNOS installation, on this folder as the project.
