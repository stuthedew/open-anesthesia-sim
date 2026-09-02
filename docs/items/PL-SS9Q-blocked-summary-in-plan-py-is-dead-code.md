---
id: PL-SS9Q
title: blocked_summary() in plan.py is dead code duplicating what docket list already prints
priority: P3
effort: S
classes: infra
status: done
feature: dev-tooling
touches: subprojects/docket
added: 2026-09-02
closed: 2026-09-02
---

**Problem.** `plan.py` defined `blocked_summary()`, "blocked items and what
they are waiting on, for a grooming pass". Nothing called it — no command, no
test, no export. Found while checking whether blocked work is visible anywhere
after `PL-YHF1` let a blocked item leave the top band.

**Why it matters.** Small, but it answers the visibility question falsely in
both directions. Reading `plan.py` suggests there is a blocked-work view and
that a grooming pass has one to call; there is neither. Meanwhile `bin/docket
list` already prints every blocked item, marked `blocked` and `safety-tagged`,
ranked by priority — so the need it was written for is met, and the function
is duplicated logic rather than a missing feature half-built. `CLAUDE.md`
holds the workflow apparatus to working reliably and staying streamlined;
this is the kind of thing that means.

**Where.** `subprojects/docket/src/docket/plan.py`.

**Fixed.** Deleted. `bin/docket list` is the blocked-work view; it needs no
second one.

**Done when.** The function is gone and nothing regressed.
