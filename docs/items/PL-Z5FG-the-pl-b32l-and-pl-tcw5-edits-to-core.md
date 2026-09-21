---
id: PL-Z5FG
title: The PL-B32L and PL-TCW5 edits to core/parameters.py shifted line numbers cited by PL-0NQ1 and PL-HXKC, which is PL-J7C5's hazard arriving again from an unrelated branch
priority: P3
effort: S
status: dropped
classes: docs
feature: dev-tooling
touches: docs/items
added: 2026-09-13
closed: 2026-09-21
reason: `.claude/rules/citation-drift.md`'s line-anchor ban, with the closed-brief clause covering half of it. Both routes this item's decision named are closed: repairing the six citations in place is what the ban refuses, and folding them into `PL-J7C5` is impossible because `PL-J7C5` is `done`. `PL-0NQ1` is `done` too, so its three citations are a historical record the clause says not to repair. Nothing is lost on the live half: `PL-HXKC` is open, all eight of its citations already named their symbols beside the numbers, and `PL-PT7M`'s commit struck the numbers and kept the symbols - the form the rule prescribes. Two of those symbols had themselves drifted (`require_concentration_fraction` is now `require_fraction`; `apply_blood_uptake` is gone), and both are marked in `PL-HXKC` for whoever takes it. Re-judged in `PL-PT7M`'s pass, 2026-09-21
---

**Problem.** The PL-B32L and PL-TCW5 edits to core/parameters.py shifted line numbers cited by PL-0NQ1 and PL-HXKC, which is PL-J7C5's hazard arriving again from an unrelated branch

**Why it matters.** Not the general finding - `PL-J7C5` (cite symbols rather
than line numbers in the queue's briefs) already holds that, and `PL-38PN`
and `PL-JXVD` hold two earlier instances. This records what a single
unrelated branch did to the citations in one sitting, which is the evidence
`PL-J7C5` is arguing from: the shift was not caused by anyone working on the
cited items, was invisible to `make check` (which passed clean, `tools/doc_check.py`
verifying that a cited *path* exists but not that a cited *line* still holds
the symbol), and nothing would have told the next session reading either
brief that the numbers had moved.

**Measured 2026-09-13, against `origin/main` at `ce020b2`.** The comment
added above `FLOW_FRACTION_TOLERANCE` and the `try`/`except` wrapper added to
`_load_packaged_json` moved everything below them in
`src/anesthesia_sim/core/parameters.py`:

| Cited in | Citation | Was | Now |
| --- | --- | --- | --- |
| `PL-0NQ1` | `parameters.py:36` (the tolerance) | 36 | 47 |
| `PL-0NQ1` | `parameters.py:274-286` (the sum-to-one validator) | 489 | 500 |
| `PL-0NQ1` | `core/patient.py:20,36` | 17, 48 | the definition is gone; the guard is at 50 |
| `PL-HXKC` | `parameters.py:427` `parse_agent_parameters` | 427 | 438 |
| `PL-HXKC` | `parameters.py:456` `parse_reference_adult_parameters` | 456 | 467 |
| `PL-HXKC` | `parameters.py:501` `load_agent_parameters` | 501 | 555 |

`PL-0NQ1`'s `274-286` and `20,36` were already wrong before this branch, so
two of the six rows are older drift that this one merely deepened - which is
itself the point, since nothing distinguished the two states to a reader.

`PL-TCW5` also deleted `core/patient.py`'s own `FLOW_FRACTION_TOLERANCE`
definition, so `PL-0NQ1`'s "`core/patient.py:20,36` enforces the same bound
independently" now describes a module that imports the constant instead. The
sentence's *claim* is still true - the guard is still independent - but the
citation no longer resolves to anything.

**Where.** `docs/items/PL-0NQ1-*.md`, `docs/items/PL-HXKC-*.md`.

**Decision needed.** Whether to repair these six citations now or to fold
them into `PL-J7C5`, which would replace the line numbers with symbol names
and make the whole class checkable rather than fixing one instance of it.
Folding in is the stronger answer if `PL-J7C5` is being worked soon; repairing
now is right if it is not, because both cited items are open and a session
picking either one up reads the wrong numbers in the meantime.

**Done when.** The six citations in `PL-0NQ1` and `PL-HXKC` resolve to what
they claim - repaired in place, or replaced with symbol names as part of
`PL-J7C5` - and whichever route was taken is recorded on `PL-J7C5`, so the
next drift of this kind is not measured a fourth time.
