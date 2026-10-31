# Roombook, an AGNOS demonstration

> **This history is simulated.** The people, their commits, the dates, the public holidays, the
> Verification outputs written in the plans and the friction metrics are made up to show how the AGNOS
> process looks when a team has used it for two months. Nothing here was really done by these people.

This repository holds the development of a small product, **Roombook**, following the process. AGNOS itself
is not stored here: `agnos-init` added it, so `CLAUDE.md` and `AGENTS.md` hold only a block pointing to the AGNOS repository
beside this folder (`../agnos-lightweight-process`). Read this repository to see what the process produces, run the AGNOS
skills against it to test them, or start an agent session in it with that repository in place.

## The product

A meeting-room booking service in Python (`service/`) with a TypeScript HTTP client and command-line tool
(`client/`), and a small server-rendered web interface (`client/src/ui/`). As the product now has a user
interface, it has a design system: every colour, size and spacing comes from the tokens of
`client/design/tokens.json`, and the stylesheet is generated from them.

| Session | Feature | What it delivers |
|---|---|---|
| BKG | FTR-BKG-001, FTR-BKG-002 | Rooms, reservations, overlap/capacity/closed-room rules, cancellation, durable storage |
| NTF | FTR-NTF-001 | Creation event, reminders before the meeting, retries on failure |
| CLI | FTR-CLI-001 | HTTP/JSON API, typed client, command-line tool |
| DSN | FTR-DSN-001 | Design system: three-tier tokens, contrast and literal checks, stylesheet generated from the tokens |
| WEB | FTR-WEB-001 | Web interface: rooms, booking, cancellation, worded refusals, unavailable service |

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
| UX designer | `-ux` | rob-ux | the design system (tokens, component catalogue), the screens, design fixes |

## Timeline

Monday 2026-08-24 to Friday 2026-10-23, Europe/Paris, working days only, 09:00 to 18:00. Two fictitious public
holidays are declared in [docs/WORKING_CALENDAR.md](docs/WORKING_CALENDAR.md). Each session is developed on a
`feature/<TRI>` branch merged into `main`: BKG 08-24 to 09-18, NTF 09-21 to 10-02, CLI 10-05 to 10-23. The UX
work runs in parallel with the CLI session: DSN (the design system) starts from `main` after the NTF merge, 10-05
to 10-15, and WEB (the interface) starts from the typed client of the CLI session, merges DSN first, and is merged
into `main` on 10-23.

## Explore

```
git log --author=-qa --format="%h %ad %an %s" --date=short     # everything done by testers
git log --author=-po --format="%h %ad %an %s" --date=short     # everything done by product owners
git log --author=-ux --format="%h %ad %an %s" --date=short     # everything done by the UX designer
git log --grep=TASK-BKG-007 --format="%h %an %s"               # the commits of one task
git log --graph --oneline --all                                 # the sessions and their merges
```

## Run the tools

```
cd service && python -m unittest discover -s tests -t .         # Python tests (standard library only)
cd client && node --test "tests/*.test.ts"                      # TypeScript tests (Node 22.18 or later)
cd client && npm run ui                                       # web interface on http://127.0.0.1:3000 (ROOMBOOK_URL names the service)
```

The AGNOS skills `agnos-index` and `agnos-trace` run from an AGNOS installation, on this folder as the project.
