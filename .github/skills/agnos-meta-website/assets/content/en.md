<!--
FTR-WEB-001: RQ-WEB-003 to RQ-WEB-012 / ADR-WEB-001: DEC-WEB-003. AGNOS website, English text.
Edit the words freely; keep the structure, then build again with the agnos-meta-website skill.
- "## <section>" opens a page element, "### <field>" one of its texts. Keep these ids identical in en.md and fr.md:
  the build refuses a field missing from one language, or unknown to the page template.
- A field is one paragraph, a list of "- " items, an index excerpt between two ``` lines (lines starting with @ are
  dimmed), or one image: ![alternative text](screens/<file>.png)
- Inline: *emphasis*, **strong**, `code`, [link text](address). End a line with \ to force a line break.
- {{link.<name>}} is replaced by an address whose name is listed in assets/site.json and whose address comes from the repository's assets/links.json (RQ-WEB-020, RQ-DOC-007);
  write no address that links.json declares.
- Comments like this one are ignored.
-->

## page

### title
AGNOS - Agentic efficiency by traceability

### description
AGNOS, a lightweight engineering process for AI-native development teams.

## notice

### label
Demo

### text
The views on this page come from Roombook, the AGNOS demo project, whose team and two months of history are simulated.

## brand

### name
AGNOS

### tagline
Agentic efficiency by traceability

## nav

### tour
The tour

### start
Get started

### demo
Demo

### sections
Sections

### language
Language

### english
EN

### french
FR

## marketplace

### label
AGNOS marketplace

## hero

### kicker
Engineering process for agentic AI

### title
AI agents write the code, or much more.\
*You keep control.*

### text
AGNOS is a lightweight, tooled process for *AI-native* development teams (pods of a few people, or solo). Requirements, decisions, tasks, code and commits carry the same identifiers: the work stays explainable, and the process is measured on every project, in real time, with the built-in AGNOS Performance Center application.

### cta-demo
Open the demo Performance Center

### cta-tour
The tour

### tools
Works with Claude Code and GitHub Copilot (OpenAI Codex support coming soon). Its artifacts are in Markdown, versioned in git, to maximise operational efficiency.

## chain

### title
The agentic loop, from need to commit

### mode-mixed
Mixed

### mode-on
End-to-end supervision

### in-loop
Human in the loop

### in-loop-text
The agent drafts; you decide and approve each step.

### on-loop
Human on the loop

### on-loop-text
The agent carries out the approved task; you supervise, and step in if needed.

### on-loop-draft-text
Asked to work in full autonomy, the agent drafts and takes the decisions; you supervise, and step in if needed.

### approve-on
Decisions delegated to the agent

### requirement
Requirement

### requirement-text
The expression of the need, formalised to be testable

### decision
Architecture and decision

### decision-text
Why this design, and what was ruled out

### task
Task

### task-text
Sized to the risk, approved before it starts

### approve
You approve

### code
Tests, then code

### code-text
Every element cites its identifiers

### done
Checklist passed

### commit
Commit

### commit-text
One per task, its identifiers checked by a script

### measure-text
End-to-end supervision of the process, across the whole project

### foot
Work is done in sessions: one functional area, one branch, ten tasks at most, for optimal context management

### supervision
Supervision

### requirement-id
RQ-BKG-003

### decision-id
DEC-BKG-002

### task-id
TASK-BKG-003

### code-id
OverlapRule.check

### commit-id
12dc6e4

### measure
Performance Center

## tour

### eyebrow
The tour

### title
The Performance Center: your agentic development at a glance

### text
The five views of the Performance Center meet the fundamental need to monitor your development.
Each example view below is a screenshot of the Performance Center on Roombook, the AGNOS demo project. Click one of them to open it, live, in the demo.

## labels

### see
What you see

### why
What makes it possible

## matrix

### view
Matrix view

### question
Was everything we asked for actually built?

### see
The end-to-end traceability matrix, from functional capabilities to code, on a single page, directly exportable.

### why
Every element of the process is uniquely identified, from the functional capability to the commit. The specification and the tests, expressed in testable syntaxes (*EARS*, *Gherkin*), keep the agent's interpretation at implementation to a minimum.

### tags
- EARS
- Gherkin
- Identifiers in the code

### shot
![Matrix view](screens/matrix.png)

### caption
The Matrix view of the Performance Center

## examples

### requirement
![A requirement](screens/example-requirement.png)

### requirement-caption
A requirement

### adr
![Architecture Decision Record, and auto-generated diagrams](screens/example-adr.png)

### adr-caption
Architecture Decision Record, and auto-generated diagrams

### plan
![Execution plan and implementation task](screens/example-plan.png)

### plan-caption
Execution plan and implementation task

### zoom
Enlarged example

### close
Close

## graph

### view
Graph view

### question
Why does this code exist, and what would a change touch?

### see
The dependency tree of a selected element: its feature, the decisions that shaped it, the tasks that delivered it, the files and functions that implement it.

### why
The synergy of the implementation's abstract syntax tree (*AST*) and of the single identifier grammar guarantees a holistic, explorable view of the relations between artifacts.

### tags
- Abstract Syntax Tree
- Identifier grammar
- Explorable graph

### shot
![The Graph view of the Performance Center](screens/graph.png)

### caption
The Graph view of the Performance Center

## history

### view
History view

### question
Who changed what, and when? Agent, human, or both?

### see
Every change to a requirement, a decision, a file or a function, credited to its authors from git. Each identity is classed as human or AI agent. Every commit, human, agentic or collaborative, can be traced through a requirement view or an implementation view.

### why
One commit per task, made by a skill that writes the task and ADR identifiers into its message, following the *Conventional Commits* standard. Git remains the single system of record, independent of any infrastructure.

### tags
- Chronological view
- One commit per task
- Human or agent

### shot
![The History view of the Performance Center](screens/history.png)

### caption
The History view of the Performance Center

## delivery

### view
Delivery view

### question
What was delivered, and how fast? Is agentic velocity under control?

### see
The tasks delivered over time, weighted by their tier, and the friction of each session: questions the agent had to ask, error recoveries, re-tiered tasks, discrepancies caught at verification.

### why
Work is done in sessions of ten tasks at most, for optimal use of the context. Each session closes on its friction counters; if one of them is not zero, a self-improvement step proposes rules for the project, applied once approved and within a defined budget.

### tags
- Sessions
- Friction counters
- Self-improvement

### shot
![The Delivery view of the Performance Center](screens/delivery.png)

### caption
The Delivery view of the Performance Center

## quality

### view
Quality view

### question
Is traceability guaranteed, per functional area?

### see
Easy-to-read KPIs from A to E, computed from risk-weighted checks. Each gap points to the element to fix: on Roombook, functions that do not cite a requirement yet.

### why
Gates the agent cannot bypass. Each task answers a need, starts only once approved (Definition of Ready) and closes only once its checklist is passed (Definition of Done). Its tier, (S)mall, (M)edium or (L)arge, scales the ceremony to the risk of the change. A failing check is allowed one fix, then the agent stops and reports.

### tags
- Definition of Ready
- Definition of Done
- Tiers S, M, L

### shot
![The Quality view of the Performance Center](screens/quality.png)

### caption
The Quality view of the Performance Center

## more

### eyebrow
Behind the views

### title
Three more reasons why it holds at scale

## index-card

### title
Designed for agents: the index

### text
A script indexes every artifact, one line each, with its exact location. The agent reads this small file first and opens only the useful lines. It takes the next free identifier from it: none is ever duplicated. The Performance Center reads the same index: what the agent sees and what you measure cannot diverge. The index is recomputed automatically, at the start of every session and before every commit, by a deterministic skill.

### caption
Roombook: an excerpt of the index.

### excerpt
```
@agnos-process/1.requirements/FTR-BKG-001-room-reservation.md
RQ-BKG-003|42-56||Double booking rejection
@agnos-process/3.plan/PLAN-BKG-001-core-booking.md
TASK-BKG-003|50-66|Done|Implement overlap rule
```

## id-card

### title
Exact links, not resemblances

### text
Every requirement, decision, task and function carries a unique identifier, and each element cites those it depends on, like a primary key and its foreign keys in a database. The agent therefore follows exact links instead of guessing, by semantic proximity, which text relates to what. The same inputs give the same links: the agent's work becomes more deterministic, and verifiable.

### foreign-key
Foreign key

### cites
cites

### primary-key
Primary key

### requirement
```
### RQ-BKG-003: Double booking rejection
```

### task
```
### TASK-BKG-003: Implement overlap rule
- Requirement refs: ==RQ-BKG-003==
- ADR refs: ADR-BKG-001 (DEC-BKG-002)
```

### adr
```
# ADR-BKG-002: Initial reservation storage
Motivated by: RQ-BKG-002, ==RQ-BKG-003==, RQ-BKG-005 (FTR-BKG-001); builds on ADR-BKG-001.
### DEC-BKG-003: In-memory dictionary for reservations
```

### semantic
Semantic matching: a probable link

### exact
Identifier: an exact link

### code
```
@service/roombook/rules/overlap_rule.py
# ==RQ-BKG-003==, DEC-BKG-002 (ADR-BKG-001)
class OverlapRule:
    """Rejects an interval that overlaps an existing reservation (==RQ-BKG-003==)."""

    def check(self, room: Room, request: ReservationRequest, existing: Sequence[Reservation]) -> None:
        """Raise ReservationConflict naming the first overlapping reservation (==RQ-BKG-003==)."""
```

### graph
TASK-BKG-003, ADR-BKG-002 and overlap_rule.py all cite RQ-BKG-003

### task-id
TASK-BKG-003

### requirement-id
RQ-BKG-003

### adr-id
ADR-BKG-002

### requirement-title
Double booking rejection

### task-title
Implement overlap rule

### adr-title
Initial reservation storage

### file-id
overlap_rule.py

### file-title
OverlapRule


## design-card

### title
Interfaces under the same control

### text
A project with a user interface defines its design system from the AGNOS template, before its first screen, as a requirement and an architecture decision.
The design system is a specification like any other, expressed as design tokens and implemented in code.

### primary-name
Primary

### primary-tokens
```
button.primary.background
→ colour.accent.default
→ colour.blue.600 = ==#2563eb==
```

### primary-css
```
.button-primary {
  background: var(--button-primary-background);
  color: var(--button-primary-text);
}
```

### primary-button
Book this room

### danger-name
Danger

### danger-tokens
```
button.danger.background
→ colour.error.strong
→ colour.red.700 = ==#b91c1c==
```

### danger-css
```
.button-danger {
  background: var(--button-danger-background);
  color: var(--button-danger-text);
}
```

### danger-button
Cancel this reservation

### caption
Buttons of the Roombook project, using the specified design tokens.

## close

### title
See it on a real project

### text
The demo page contains all the views, all the links and all the commits of Roombook's two simulated months.

### address
Generated by agnos-perf-center on Roombook, and published with this site.

### cta
Open the demo Performance Center

## start

### title
Three steps to the first session

### step1-title
Install the plugin

### step1-text
A single marketplace for Claude Code and GitHub Copilot (OpenAI Codex support coming soon).

### step1-command
```
claude plugin marketplace add {{link.marketplace}}
claude plugin install agnos@agnos-marketplace
```

### step2-title
Add AGNOS to a project

### step2-text
One call to `agnos-init`. Your own files remain intact.

### step2-command
```
Call the agnos-init skill.
```

### step3-title
Start a session

### step3-text
In a new conversation, the agent records the session and opens its branch.

### step3-command
```
Start a new AGNOS session, trigram <TRI>.
```

## footer

### developers
For your developers: the documentation on GitHub

### license
AGNOS is distributed under the GNU Affero General Public License v3.
