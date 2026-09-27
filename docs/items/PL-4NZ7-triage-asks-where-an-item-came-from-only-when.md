---
id: PL-4NZ7
title: Triage asks where an item came from only when it is triaged into the workflow lane, so an apparatus item that a missing workflow_paths entry leaves crossing or product is never asked for a generator
status: untriaged
touches: .claude/skills/docket/modes/triage.md
added: 2026-09-27
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
