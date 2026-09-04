---
id: PL-KCQ7
title: 40 percent of the suite's wall clock (29.2 s of 70 s) tests subprojects/docket, so the workflow apparatus dominates the simulator's own gate
status: done
priority: P2
effort: S
classes: session-cost, planning
feature: dev-tooling
touches: Makefile
verify: python3 tools/doc_check.py check && grep -qF 'deleting the whole docket suite would have returned' Makefile
added: 2026-09-03
closed: 2026-09-04
---

**Problem.** `subprojects/docket/tests` is 29.8 s of the 79.5 s `pytest` line and
about a quarter of the whole gate, so the workflow apparatus costs more of the
simulator's check than any single part of the simulator does. The project owner
asked the question that follows from it (2026-09-04): should docket come off the
uniform Class C bar, and would fewer checks there be faster without costing bugs?

**Measured.** The whole gate, this four-core container, warm caches, 2026-09-04:

| step | wall |
| --- | --- |
| `ruff format --check` | 0.1 s |
| `ruff check` | 0.0 s |
| `mypy` (strict, repo-wide) | 6.9 s |
| `tools/ignore_check.py` | 2.1 s |
| `pytest --cov` (serial, as it then was) | 79.5 s |
| - of which `tests/` | 49.3 s |
| - of which `subprojects/docket/tests`, 532 tests | 29.8 s |
| `bin/docket check` | 33.3 s |
| `doc_check.py` and `contrast_check.py` | 0.2 s |
| **total** | **~122 s** |

**Answer: no, on all three parts of the question.**

**There is no classification to move it off.** IEC 62304 classifies items of the
*medical device software system*; a backlog tool that never runs in the product
and computes no displayed value is outside its scope rather than Class A within
it. The only place this project was ever going to write a class down is
`PL-BLHV`, still `needs-decision`, and its subject is the application. Re-classing
changes no check either way, because the gate is set by `Makefile` and not by a
letter. `CLAUDE.md` already holds this tree to the lower of its two standards -
"working reliably and staying streamlined" against the specialist standard for
`src/`, `tests/`, `docs/MODEL.md` and `README.md` - which is the tier the question
was asking for, in the place where it does some work.

**The gate is already tiered, and docket is already on the low tier.** The one
Class-C-grade check in it - 100% of statements *and* branches - is scoped to
`anesthesia_sim.core`. docket has no coverage floor at all. What still reaches it
is `ruff` at 0.1 s and `mypy` at 6.9 s repo-wide, so there is nothing left to
relax except the tests themselves.

**Cutting those tests would cost bugs.** 63 of the store's 125 `defect`-classed
items touch `subprojects/docket` - about half this project's defects, out of
~3,600 source lines - and **39 of the 63 describe a silent failure**: the check
passed and the wrong answer was delivered anyway. Two of them corrupted the
safety classification itself. `PL-BR4G`: `parse_front_matter` silently kept the
last of a duplicate key, so a corrupt item passed `docket check`. `PL-MVC2`:
nothing checked `classes` against a vocabulary, so `classes: safey` left
safety-critical work seatable in the bottom band with zero errors reported. That
is precisely the failure class human use does not catch and a test does.

The governing standard for a tool of this kind is not IEC 62304 at all but
ISO 13485:2016 clause 4.1.6 - validate software used in the quality system, and
make the validation proportionate to the risk of its *use*. docket's risk is not
patient harm; it is silently mis-recording the safety class of product work,
which the two items above are worked examples of. Proportionate validation for a
tool with that history is roughly what it already has.

**There is no fat to trim either, only coverage.** The 12 slowest docket tests
sum to 13.7 s; the remaining ~520 spend ~16 s at roughly 30 ms each, which is
`git` subprocess startup spread thin rather than a few slow tests. So cutting
time there means cutting coverage broadly. Moving the suite out of the default
run to CI-only was considered and rejected for the same reason: against a
39-instance silent-failure history, the session editing docket is exactly the one
that has to see the failure.

**What was done instead.** `PL-WCZV` - `pytest -n auto` on the `check` target and
the CI job. It returns 54.8 s of the 122 s gate against the 29.8 s that deleting
the entire docket suite would have returned, and it removes no check: 1224 passed
and coverage byte-identical at 100% in both modes.

**Done when.** The measurement and the answer are recorded where the next session
asking this question will meet them, and the wall clock is addressed by something
that removes work rather than checks.
