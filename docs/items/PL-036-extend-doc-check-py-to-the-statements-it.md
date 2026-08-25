---
id: PL-036
title: Extend `doc_check.py` to the statements it currently cannot decide
priority: P2
effort: M
status: needs-decision
classes: docs, infra, session-cost
feature: dev-tooling
touches: docs/MODEL.md, tools/doc_check.py
added: 2026-08-24
---

**Problem.** `tools/doc_check.py` checks that cited things *exist*. It
cannot check that a sentence about them is *true*: a `must` in
`docs/MODEL.md` the code no longer satisfies, a shipped feature still
described as deferred, a displayed value whose units the interface changed.
**Why it matters.** Those are the remaining close-out failure modes, and
they are the ones with clinical consequence — `CLAUDE.md` calls a stale
statement about what a value means a safety issue, not tidiness.
**Where.** `tools/doc_check.py`, `docs/MODEL.md` ("Required invariants",
"Minimum displayed outputs").
**Decision needed.** Whether any of it is mechanizable without producing
confident nonsense. One candidate is concrete: `docs/MODEL.md`'s "Minimum
displayed outputs" could name the `SimulationSnapshot` field behind each
displayed value, making the list checkable against the dataclass the way the
provenance table is now checkable against the JSON. Whether the `must`
statements can be tied to named tests is the harder half.
**Done when.** Either a further check is implemented, or the decision that
this half stays human is recorded with its reasoning.
