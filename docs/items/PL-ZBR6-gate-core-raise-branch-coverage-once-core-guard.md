---
id: PL-ZBR6
title: Gate core/ raise-branch coverage once core-guard-coverage finishes
priority: P3
effort: S
status: ready
classes: infra, test
feature: dev-tooling
touches: pyproject.toml
added: 2026-08-25
---

**Problem.** Uncovered `raise`/`except` branches in the scientific core are
found only when someone runs a coverage report. Nothing holds the line once
they are covered.

**Why it matters.** Those branches are the guards that refuse impossible
inputs and halt untrustworthy runs. A guard with no test is a guard nobody has
shown fires.

**Where.** `pyproject.toml` (coverage configuration), CI.

**Notes.** From PL-B043. Deliberately **narrow**: a targeted rule — every
`raise` in `src/anesthesia_sim/core/` covered — rather than a global
percentage threshold, which is a blunt instrument that manufactures busywork
tests.

**Do not start before its precondition.** `core-guard-coverage` is at 7 of 9. Turning a gate
on now red-builds against two items that are already open and already
assigned. This starts when that feature finishes.

**Done when.** An uncovered `raise` in `core/` fails the build, and the gate
was switched on against a green tree.
