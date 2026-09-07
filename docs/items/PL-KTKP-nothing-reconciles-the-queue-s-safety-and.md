---
id: PL-KTKP
title: Nothing reconciles the queue's safety- and science-classed items against the frozen gate list, so eleven owed re-entries sat unrecorded
priority: P2
effort: M
status: done
classes: defect, infra
feature: planning-cadence
touches: ROADMAP.md, docs/ARCHITECTURE.md, tools/doc_check.py, tests/unit/test_doc_check.py, docs/items
added: 2026-09-07
closed: 2026-09-07
verify: python3 tools/doc_check.py check && grep -q 'def check_gate_reentries' tools/doc_check.py
---

**Problem.** Nothing reconciles the queue's safety- and science-classed items
against the frozen gate list, so eleven owed re-entries sat unrecorded.

`ROADMAP.md` states one unconditional rule in two places — "The cadence" step 4
("a finding made while clearing or implementing goes to the next gate unless
the problem it describes predates the freeze ... or is `P0`/`safety`/`science`,
either of which re-enters this one") and "The gate is a snapshot, not a moving
target" ("Two further exceptions re-enter the current gate regardless of
presence: anything at `P0`, and anything classed `safety` or `science`").
`PL-9PMV` settled that these are one rule rather than two readings.

Gate 1 was frozen 2026-09-06 at 121 entries. Between that freeze and 2026-09-07
fifteen `safety`- or `science`-classed items were filed. Four — `PL-1XPX`,
`PL-CTD7`, `PL-W7H9`, `PL-Z3W6` — were placed in v0.5.0's `Required scope` and
so clear with the milestone. The other eleven appear nowhere in `ROADMAP.md`:

`PL-CXYT`, `PL-WT07`, `PL-5K5C`, `PL-73G7`, `PL-7HDS`, `PL-YKSM`, `PL-ZP7Z`,
`PL-XJ5P`, `PL-W21J`, `PL-61WW` and `PL-8PS6`.

**Why it matters.** The gate is the project's stated readiness measure for
v0.5.0, and it under-reported by eleven entries for two days. Worse than the
count: `docket check` pins `safety` and `science` to the top band, so those
eleven are ten of the project's eleven open `P1` items, while the 84 open
entries the gate *did* hold are all `P2` and `P3`. A reader asking "what is left
before v0.5.0" was shown a list from which every `P1` had been omitted, and
`bin/docket wave`'s "84 of 121" was arithmetically correct against the written
list the whole time — the silent-wrong-answer shape `CLAUDE.md` names as
earning an interruption.

The mechanism to record a re-entry already exists and was used twice on the
freeze day itself — the groups "Added 2026-09-06 under the presence rule" and
"Added 2026-09-06 after `PL-NBWP` closed", the second citing this exact
unconditional exception. So the failure is not a missing procedure. It is that
the procedure runs only when a session happens to think of it, and between
2026-09-06 and this item nobody did. It surfaced because the project owner
asked for the gate's status by hand.

**The decidable half, and the half that is not.** Whether an open
`safety`/`science` item is placed by the current gate's section is decidable:
`docket.roadmap.MilestoneSection.scope_ids` already names the ids a section
*places* — its frozen list plus its `Required scope` — and excludes an id the
section merely mentions, which is the distinction `PL-NBCS` records. What is
not decidable is whether an unplaced one should join the frozen list, be placed
in `Required scope`, or be deferred with a recorded reason under the discretion
"The gate is a snapshot" grants. So this is an advisory rather than an error:
it names what is unplaced and leaves the placement to the session.

**Where.** `ROADMAP.md` § "v0.5.0 - the case you can branch" → "Debt gate: the
frozen list"; `tools/doc_check.py`, beside `check_gate_counts`, which already
holds the list's arithmetic to itself and is the natural place for a check that
holds its *membership* to the queue.

**Done when.** The eleven are recorded in `ROADMAP.md` under a dated group
citing the rule they re-enter under, with the four excluded ones and the reason
they are excluded; every count `check_gate_counts` reads agrees; and
`python3 tools/doc_check.py check` raises an advisory naming any open
`safety`- or `science`-classed item the current gate's section does not place.

**Found.** Answering the project owner's "status of gate" on 2026-09-07, by
comparing the queue's classes against the ids written into `ROADMAP.md`.
