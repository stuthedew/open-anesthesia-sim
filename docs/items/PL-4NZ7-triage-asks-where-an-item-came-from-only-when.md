---
id: PL-4NZ7
title: Triage asks where an item came from only when it is triaged into the workflow lane, so an apparatus item that a missing workflow_paths entry leaves crossing or product is never asked for a generator
priority: P1
effort: S
status: ready
classes: defect
touches: .claude/skills/docket/modes/triage.md, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_cli.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-28 triage pass
added: 2026-09-27
payoff: every capture touching an apparatus path is asked where it came from, so a generator reached through a crossing item is found instead of queued
verify: grep -q 'def test_triage_marks_a_crossing_item_as_owing_a_generator_check' subprojects/docket/tests/test_cli.py
impairs-generators: render.format_triage marks no untriaged item as owing a Generator check, and triage.md keys that check on Item.lane being workflow, so an apparatus-generated capture that also touches a simulator path is never asked where it came from
---

**Problem.** Triage asks where an item came from only when it is triaged into the workflow lane, so an apparatus item that a missing workflow_paths entry leaves crossing or product is never asked for a generator

**Evidence, 2026-09-27, at `553522c6`.** `.claude/skills/docket/modes/triage.md`
§ "Ask every workflow-lane item where it came from" opens: "**Each item triaged
into the workflow lane is scrutinized for an unresolved generator**". The
lane is `Item.lane`, which reads every path `workflow_paths` does not list as
the simulator's (`PL-8ZGY`). So an apparatus item that touches an unplaced
path - `docs/resident-instructions.md`, `bin/docket`, the root `conftest.py`
until `#1199` - triages as `crossing` or `product` and is never asked where it
came from. `PL-8ZGY`'s generator went unfound until a session happened to
notice, and this is one route by which it could.

**Why it is filed apart from `PL-8ZGY`.** Fixing `PL-8ZGY` shrinks the set this
misses but does not close it: an item can be genuinely `crossing` and still be
apparatus-generated. The question is whether the scrutiny should key on the
lane at all, or on the item's apparatus paths.

**Whether it ranks as a generator-machinery defect** (`impairs-generators:`)
is triage's call. It breaks identification rather than ranking, but it is a
skill procedure, and `generator_paths` names code, not skills.

**Why it matters.** A capture touching both an apparatus path and a simulator
path triages as `crossing` and is never asked where it came from, so a
generator reached through one is queued rather than found. `PL-8ZGY` (#1210)
closed the route this capture names, an unplaced path, but not this one: the
scrutiny still keys on the lane.

**Decided at triage, 2026-09-28: recorded as `impairs-generators:`**, the rank
`CLAUDE.md` gives a defect in finding generators (`PL-4MPJ`). The decidable half
goes in code: `bin/docket triage` marks each item whose `touches` name a path
`workflow_paths` places as owing a Generator check, whatever its lane, and the
section in `triage.md` keys on that mark rather than on the workflow lane.

**Done when.** `bin/docket triage` prints the mark for a `crossing` item, held
by a test, and `.claude/skills/docket/modes/triage.md` no longer keys the check
on the workflow lane.

**Generator check.** Not a member of any head: it is the identification
machinery itself, recorded under `impairs-generators:`.
