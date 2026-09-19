---
id: PL-G5ZH
title: A defect in the machinery that identifies and ranks generators has no way to say so, so it ranks on its band alone while every generator it fails to surface keeps running
priority: P2
effort: M
status: done
classes: infra
feature: generator-machinery-rank
milestone: v0.4.28
touches: subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/config.py, subprojects/docket/src/docket/plan.py, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_model.py, subprojects/docket/tests/test_plan.py, subprojects/docket/tests/test_checks.py, subprojects/docket/README.md, docket.toml, CLAUDE.md, .claude/skills/docket/SKILL.md, docs/items
added: 2026-09-19
closed: 2026-09-19
pr: 700
verify: uv run pytest subprojects/docket/tests/test_plan.py subprojects/docket/tests/test_model.py subprojects/docket/tests/test_checks.py -q && grep -q 'def test_a_generator_machinery_defect_ranks_with_a_generator' subprojects/docket/tests/test_plan.py
---

**Decision (project owner, 2026-09-19).** A defect in the root-cause/generator
identification and prioritization system ranks at **the same priority as a
generator** - directly below `P0` and above every band, on the tier `PL-VX5H`
built. Specified in the owner's own words, not a session's recommendation.

**Problem.** The tier has one entrance and it is `root-cause-of:`, which names
the items a mechanism causes. A defect *in the machinery that reads that field*
names no items, so it cannot claim the tier and ranks on its band alone.
`PL-C97K` - `docket show` prints no reverse edge, so a session opening a member
cannot see a generator is deciding its scope - sits at `P2`, below every `P1`,
while the identification half of the system it breaks is what puts generators
on the tier at all.

**Why it matters.** A generator earns the tier because three items stand on
it and every session it stands through pays it again. A defect in the machinery
is that argument one level up: while identification is broken, generators are
not recorded, and an unrecorded generator is not ranked by anything. The
suppressed cost is unbounded in the same way and invisible in a worse one -
nothing in the store says a generator went unfound.

**Two designs counted and refused, 2026-09-19.**

- *Derive it from `touches`* - promote any item touching the machinery files.
  Counted against this store: **36 of 322 open items** (20 `P2`, 16 `P3`) touch
  `plan.py`, `model.py`, `checks.py`, `render.py`, `cli.py` or
  `generator_check.py` for unrelated reasons. That is the failure
  `tools/generator_check.py`'s own docstring names for citation density - "33
  items ... promoting all of them would mean nothing". The files are shared; the
  machinery inside them is a few functions.
- *Hand-promote the band* - file such a defect at `P1` or `P0`. Refused by an
  existing decision: `PL-VX5H` records the owner on band promotion, *"We
  constantly add more P1 as we develop, so these never get done and the bugs
  pile up."* `P0` is a clinical hotfix and diluting it with apparatus work is
  worse.

**Adopted: a recorded claim with a cheap falsifier**, which is `root-cause-of:`'s
own shape. A new front-matter field `impairs-generators:` holds, in prose, which
function of the system is impaired; presence is the claim and the text is the
audit trail, exactly as `not-delegable:` works, and a bare `yes`/`no` is
rejected for the same reason. The judgment stays the session's - nothing infers
it. The falsifier is deterministic: the item's `touches` must reach a path in a
new `generator_paths` config setting, so a claim on an item that touches none of
the machinery is a `docket check` error rather than a free promotion. `touches`
cannot decide the claim (36 items) but it can refute one, which is the same
division `root_cause_faults`' three-item floor already draws.

**Traffic, stated rather than hidden.** One open item in 322 would carry the
field today. `PL-VX5H` built this tier when it was worth nothing on this tree -
*"the mechanism exists so the next generator is ranked correctly on the day it
is detected rather than after somebody notices it"* - and the same answer
applies to its entrance.

**Consequence, deliberate.** Such a defect outranks a `safety`- or
`science`-classed `P1`, because the tier does. The owner refused that carve-out
twice for generators (`PL-VX5H`, 2026-09-17) and the child rule inherits it.
`P0` still outranks both, which is where a clinical defect that must be fixed
now belongs.

**Done when.** `model.py` carries the field and a `generator_defect_faults`
predicate that `plan.py` and `checks.py` both read, so the ranking and the
checker cannot disagree; `docket next` ranks a sound claim on the generator tier
with a reason line saying so in those words and distinguishing it from a
root-cause generator; `docket check` errors on an unsound claim; `docket show`
and the session-start digest surface it; `docket.toml` declares
`generator_paths`; and tests cover the ordering against a `P0`, a
`safety`-classed `P1` and a true generator.
