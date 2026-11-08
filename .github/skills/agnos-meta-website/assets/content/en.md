<!--
FTR-WEB-001: RQ-WEB-003 to RQ-WEB-012 / ADR-WEB-001: DEC-WEB-003. AGNOS website, English text.
Edit the words freely; keep the structure, then build again with the agnos-meta-website skill.
- "## <section>" opens a page element, "### <field>" one of its texts. Keep these ids identical in en.md and fr.md:
  the build refuses a field missing from one language, or unknown to the page template.
- A field is one paragraph, a list of "- " items, an index excerpt between two ``` lines (lines starting with @ are
  dimmed), or one image written as a linked image: [![alternative text](screens/<file>.png)](<address opened on click>)
- Inline: *emphasis*, **strong**, `code`, [link text](address). End a line with \ to force a line break.
- {{index.documents}}, {{index.size}} and {{index.ratio}} are measured on the demo by the build.
- Comments like this one are ignored.
-->

## page

### title
AGNOS · Efficiency by traceability

### description
AGNOS, a lightweight engineering process for teams that build software with AI agents.

## notice

### label
Demo

### text
The views on this page come from Roombook, the AGNOS demo project, whose team and two months of history are simulated.

## brand

### name
AGNOS

### tagline
Efficiency by traceability

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

## hero

### kicker
Engineering process for agentic AI

### title
AI agents write the code.\
*You keep control.*

### text
AGNOS is a lightweight process, with its tools, for teams that build software with AI agents. Requirements, decisions, tasks, code and commits carry the same identifiers: the work stays explainable, and the process can be measured on every project.

### cta-demo
Open the demo Performance Center

### cta-tour
Take the tour

### tools
Works with Claude Code, GitHub Copilot and OpenAI Codex. Its artifacts are plain Markdown, versioned in git.

## chain

### title
One requirement, followed from need to commit

### mode-mixed
Mixed

### mode-on
On the loop throughout

### in-loop
Human in the loop

### in-loop-text
The agent drafts; you decide and approve each step.

### on-loop
Human on the loop

### on-loop-text
The agent carries out the approved task; you supervise it, and step in when needed.

### on-loop-draft-text
Told to work in full autonomy, the agent drafts and takes the decisions; you supervise it, and step in when needed.

### approve-on
Decisions delegated to the agent

### requirement
Requirement

### requirement-text
What must be true, written to be tested

### decision
Decision

### decision-text
Why this design, and what was rejected

### task
Task

### task-text
Sized by risk, approved before it starts

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
Measures the whole chain, on every project

### foot
Work runs in sessions: one functional area, one branch, ten tasks at most.

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
3aec803

### measure
Performance Center

### measure-id
Roombook

## tour

### eyebrow
The tour

### title
Five views of the Performance Center, five questions a CIO asks

### text
Each view is a screenshot of the page AGNOS generated on Roombook, its demo project. Click one to open it, live, in the demo.

## labels

### see
What you see

### why
What makes it possible

### open
Open in the demo

## stop-overview

### view
Overview

### question
Is what we asked for actually built?

### see
For each functional area, the requirements that the code cites directly, only through a task or a decision, or not at all, with the grade of the whole project.

### why
Requirements are written as testable sentences (EARS) with acceptance criteria (Gherkin). Every source file names, in a comment, the requirements it implements.

### tags
- EARS
- Gherkin
- IDs in the code

### shot
[![The Overview view of the Performance Center on Roombook](screens/overview.png)](demo/PERF-CENTER.html)

### caption
Roombook: every requirement is cited by the code that implements it.

## stop-graph

### view
Graph

### question
Why does this code exist, and what would a change touch?

### see
One requirement with everything linked to it: its feature, the decisions that shaped it, the tasks that delivered it, the files and functions that implement it.

### why
A single identifier grammar, written as comments in documents, code, tests and commit messages. Each architecture decision has its own identifier, so the code cites the exact decision it applies.

### tags
- Decision records (ADR)
- One identifier grammar
- IDs in comments

### shot
[![The Graph view of the Performance Center, centred on requirement RQ-BKG-003](screens/graph.png)](demo/PERF-CENTER.html#RQ-BKG-003)

### caption
`RQ-BKG-003`, No double booking, and everything that cites it.

## stop-quality

### view
Quality

### question
Can we trust how the process was applied?

### see
A grade from A to E, computed from checks weighted by risk. Each finding points to the element to fix: on Roombook, functions that do not cite a requirement yet.

### why
Gates the agent cannot skip. A task starts only once approved (Definition of Ready) and closes only once its checklist passes (Definition of Done). Its tier, S, M or L, scales the ceremony to the risk of the change. A failing check gets one fix, then the agent stops and reports.

### tags
- Definition of Ready
- Definition of Done
- Tiers S, M, L

### shot
[![The Quality view of the Performance Center on Roombook](screens/quality.png)](demo/PERF-CENTER.html)

### caption
The report card of Roombook, and the checks behind its grade.

## stop-history

### view
History

### question
Who changed what, and when?

### see
Every change to a requirement, a decision, a file or a function, credited to its authors from git. Each identity is classed as a human or an AI agent, and each commit as human, agent, or both together.

### why
One commit per task, made through a skill that writes the task and ADR identifiers into its message. Git stays the single system of record.

### tags
- One commit per task
- Human or agent

### shot
[![The History view of the Performance Center on Roombook](screens/history.png)](demo/PERF-CENTER.html)

### caption
Two months of Roombook's history.

### note
Roombook's simulated team is human only for now: AI agent identities will be added to the demo.

## stop-delivery

### view
Delivery

### question
What was delivered, and is the process improving?

### see
The tasks delivered over time, weighted by their tier, and the friction of each session: questions the agent had to ask, error recoveries, re-tiered tasks, discrepancies caught at verification.

### why
Work runs in sessions of ten tasks at most, so the agent's context stays clear. Each session closes on its friction counters; when one is not zero, a self-improvement step proposes rules for the project, applied once approved and within a line budget.

### tags
- Sessions
- Friction counters
- Self-improvement

### shot
[![The Delivery view of the Performance Center on Roombook](screens/delivery.png)](demo/PERF-CENTER.html)

### caption
What Roombook delivered, period by period.

## more

### eyebrow
Behind the views

### title
Two more reasons it holds at scale

## index-card

### title
Built for agents: the index

### text
A script indexes every artifact, one line each, with its exact location. The agent reads this small file first and opens only the lines it needs. It takes the next free identifier from it, so none is ever duplicated. The Performance Center reads the same index: what the agent sees and what you measure cannot diverge.

### documents
Process documents, {{index.documents}}

### index
The index, {{index.size}}

### caption
Roombook: the index is about {{index.ratio}} of the documents it describes.

### excerpt
```
@agnos-process/1.requirements/FTR-BKG-001-room-reservation.md
RQ-BKG-003|42-56||No double booking
@agnos-process/3.plan/PLAN-BKG-001-core-booking.md
TASK-BKG-003|50-66|Done|Overlap rule
```

## design-card

### title
Interfaces under the same control

### text
A project with a user interface defines its design system before its first screen, as a requirement and an architecture decision. Screens cite it, and the code reads every colour and size from a token. On Roombook, a test rejects any raw value.

### component
Component

### semantic
Semantic

### global
Global, the only raw value

### caption
A button's background, from Roombook's tokens: `FTR-DSN-001` and `ADR-DSN-001`.

### component-token
button.primary.background

### semantic-token
colour.accent.default

### global-token
colour.blue.600

### global-value
#2563eb

## close

### title
See it on a real project

### text
The demo page holds every view, every link and every commit of Roombook's two simulated months.

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
One marketplace for Claude Code, GitHub Copilot and OpenAI Codex.

### step2-title
Add AGNOS to a project

### step2-text
One call to `agnos-init`. Your own files stay as they are.

### step3-title
Start a session

### step3-text
In a new conversation, the agent records the session and opens its branch.

## footer

### developers
[For your developers: the documentation on GitHub](https://github.com/spashx/agnos-lightweight-process)

### license
AGNOS is distributed under the GNU Affero General Public License v3.
