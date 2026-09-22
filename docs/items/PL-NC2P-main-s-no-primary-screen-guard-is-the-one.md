---
id: PL-NC2P
title: `main()`'s no-primary-screen guard is the one testable line `app/main.py` leaves uncovered after the Qt port
status: ready
priority: P3
effort: S
classes: test, infra
feature: core-guard-coverage
touches: tests/unit/test_bootstrap.py, src/anesthesia_sim/app/main.py
added: 2026-08-25
---

> **Groomed 2026-09-22 (`PL-Y4YG`): the Qt port transformed this, and one line
> is left worth a test.** Retitled from "`app/main.py` sits at 47% coverage
> with no item covering it". Measured over the whole suite: `app/main.py` is
> at 92%, 24 statements with 2 missed, because `tests/unit/test_bootstrap.py`
> now drives `main()` end to end against recording fakes (`PL-005`). The two
> misses are the `raise RuntimeError("no primary screen is available to open
> the window on")` guard, which a fake application returning no screen
> reaches, and `main()` under `if __name__ == "__main__":`, which pytest
> imports rather than runs - the uncovered-by-construction case recorded
> below, at its new line. So **Done when** now reads: the guard has a test,
> and the `__main__` line is either kept with its reason recorded or removed,
> since `uv run anesthesia-sim` enters through the console script that
> `test_bootstrap.py` already pins. The **Problem** paragraph and the line
> numbers below describe the Flet-era file.

**Problem.** `src/anesthesia_sim/app/main.py` has 10 of 19 statements
uncovered (lines 16-29 and 39), and no queue item mentions it. It is the
application entry point.

**Why it matters.** Not by itself a safety path, but it is the largest
uncovered block in the package and nobody has decided whether that is
acceptable. PL-005 will touch this file (window sizing), so the question
arrives with that work whether or not it is answered first.

**Where.** `src/anesthesia_sim/app/main.py`.

**Done when.** Either the entry point is covered, or the reason it is not
practically testable is recorded here and in whatever coverage expectation the
project adopts.

**The coverage command shape does not fit this item** (recorded 2026-09-02
while working `PL-5TN8`). `uv run pytest --cov=anesthesia_sim.app.main
--cov-fail-under=100` is the shape every other `core-guard-coverage` item
took, and it cannot pass here however much test-writing is done. Measured on
this checkout: 10 of 19 statements uncovered, `16-26` and **`36`** - and 36 is
`if __name__ == "__main__": main()`, which pytest imports the module rather
than runs, so no test can reach it. Reaching 100% needs a coverage exclusion,
and whether to grant one is part of the decision this item asks for rather
than something a command can assert.

That is on top of the item already being disjunctive: "either the entry point
is covered, **or** the reason it is not practically testable is recorded".
`--cov-fail-under=100` fails forever under the second outcome, so it would be
a specification the item can be correctly done without meeting.

So when this is started, its `verify:` should be the paired shape the skill
recommends for a decision recorded in prose - something that passes today plus
a `grep` for what the work adds - not the coverage shape. Cost is then well
under a second rather than the ~56 s a full-suite `--cov` run costs.
