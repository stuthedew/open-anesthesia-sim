---
id: PL-DFLC
title: test_cli.py's test_flight_reads_below_an_uneven_horizon_by_the_landed_prefix docstring says claims._landed_through asks whether the branch's work up to a commit is content the base already holds, and since PL-927J it asks whether the base wrote it since the commit's own fork
priority: P3
effort: S
status: ready
classes: docs
feature: pre-fork-content
touches: subprojects/docket/tests/test_cli.py
added: 2026-09-27
payoff: the docstring on a test of the landed-content read explains the question the code actually asks
verify: ! grep -qF 'content the base already holds (`claims._landed_through`)' subprojects/docket/tests/test_cli.py
---

**Problem.** test_cli.py's test_flight_reads_below_an_uneven_horizon_by_the_landed_prefix docstring says claims._landed_through asks whether the branch's work up to a commit is content the base already holds, and since PL-927J it asks whether the base wrote it since the commit's own fork

**Why it matters.** The docstring tells the next reader of the landed-content
family what the test depends on, and it names the question `PL-927J` retired.

**Done when.** The docstring states the question `claims._landed_through` asks
now: whether the base wrote the content since the commit's own fork.

**Generator check.** An instance of `PL-G424`'s fact in prose its 2026-09-19 decision left open (not a citation), filed in
the commit that closed `PL-927J`, whose change moved the fact; a one-off.
