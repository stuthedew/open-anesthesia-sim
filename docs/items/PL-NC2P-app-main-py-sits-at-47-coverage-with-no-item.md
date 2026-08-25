---
id: PL-NC2P
title: `app/main.py` sits at 47% coverage with no item covering it
status: ready
priority: P3
effort: S
classes: test, infra
feature: core-guard-coverage
touches: tests/unit/test_bootstrap.py, src/anesthesia_sim/app/main.py
added: 2026-08-25
---

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
