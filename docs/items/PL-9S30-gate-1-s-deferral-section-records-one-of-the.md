---
id: PL-9S30
title: Gate 1's deferral section records one of the nine entries sequenced past v0.5.0; the other eight exist only as a blocked-by field, which the gate's own snapshot rule says must be written down and explained
priority: P2
effort: S
status: done
classes: defect, docs
feature: planning-cadence
touches: ROADMAP.md, docs/items/
added: 2026-09-13
closed: 2026-09-13
pr: 521
verify: python3 tools/doc_check.py check && grep -qF 'Sequenced past v0.5.0, so not clearable before it begins' ROADMAP.md
---

**Problem.** Gate 1's deferral section records one of the nine entries sequenced past v0.5.0; the other eight exist only as a blocked-by field, which the gate's own snapshot rule says must be written down and explained

Measured 2026-09-13 against `origin/main` at `5cbcea3`.

`ROADMAP.md` § "The gate is a snapshot, not a moving target" allows a gate
entry to be deferred only if the gate's own section "says so and says why",
and § "Deferred to v0.5.1, because the port dissolves the defect — 1 entry"
is where Gate 1 does that. It names `PL-NGF7` and nothing else.

Eight more open entries are sequenced past v0.5.0 and say so only in their
`blocked-by` field:

- `PL-3355`, `PL-Q4VH`, `PL-THXF`, `PL-TG60`, `PL-W8DQ` — carried by the Qt
  port. `ROADMAP.md` § "Fixes this port carries, and why that is not scope
  creep" names all five, so the *reasoning* is recorded; what is missing is the
  disposition in Gate 1's own section, which is the section the rule names and
  the one a session clearing the gate reads. All five still sit in groups
  headed "Cleared **before** v0.5.0 begins", which their `blocked-by` now
  contradicts.
- `PL-GS3R` — `blocked-by: v0.5.1`, `P1`, `safety`. Its gate entry still reads
  "`needs-decision`: the three routes trade resolution against the frame
  budget, and choosing is the project owner's", and that choice has since been
  made (§ "v0.5.1 — the interface moves to Qt", "`PL-GS3R` is a safety decision
  this one decides"). It also still sits under "Cleared by the `v0.4.x` track,
  ahead of this gate", which places it two steps earlier than its blocker.
- `PL-8PS6`, `PL-WZVZ` — blocked behind `PL-FG9D`, the base anesthesia-machine
  abstraction, which `ROADMAP.md` places nowhere at all. Clearing them means
  scoping that design round first, and nothing in the gate says so.

**Why it matters.** The frozen list is the artifact a session clearing the gate
works from, and for eight entries it currently disagrees with the items
themselves about when the work happens. The rule that a deferral be written
down exists precisely so the gate "cannot be renegotiated"; a deferral living
only in a `blocked-by` field is renegotiation by frontmatter.

**Where.** `ROADMAP.md` § "Debt gate: the frozen list" under "v0.5.0 - the case
you can branch" — the group headings, the `PL-GS3R` entry's prose, and the
"Deferred to v0.5.1" section's count and membership.

**Not a re-decision.** Every one of these sequencing calls is the project
owner's and already taken; this item writes them where the gate's own rule says
they belong. `PL-SL70` is the tooling half of the same finding.

**Done when.** Gate 1's own section carries a subsection naming all nine
entries sequenced past v0.5.0, each with its reason and a pointer to where the
decision was taken, and nothing is moved between groups. The six that recorded
their deferral nowhere a reader would look carry `blocked-by: v0.5.1`, and
v0.5.1's `Required scope` names the fixes it carries so `MilestoneStates.
ships_with` reads them - which is what stops `docket check` advising, on every
run, that an item waiting for the port to land is ready to promote.
