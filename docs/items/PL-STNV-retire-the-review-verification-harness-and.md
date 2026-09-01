---
id: PL-STNV
title: Retire the review-verification harness and capture its last live finding
priority: P2
effort: S
status: done
classes: defect, infra
feature: dev-tooling
milestone: v0.2.8
touches: tools/review-verification, tests/reference/test_coupled_dynamics.py, docs/WORKING_NOTES.md
added: 2026-08-30
closed: 2026-08-30
pr: 94
verify: test ! -e tools/review-verification && python3 tools/doc_check.py check
---

**Problem.** Finding P2-1 in `tools/review-verification/` has reproduced on
every run since the v0.2.0 architecture review and has never had a queue item.
PL-013 (triage the review harness's four remaining findings) closed "without
action", so the finding stayed live in a tool nobody reads and out of the queue
everybody does.

**Why it matters.** A harness that reports a real defect nobody acts on is
worse than no harness: it creates the appearance that the finding is tracked.
P2-1 is a genuine safety finding — the step-size half of it is now PL-VP7N
(refuse a simulation step outside the operator split's applicability domain) —
and it went nineteen days and three releases without being written down
anywhere a session would look.

**Where.** `tools/review-verification/`;
`tests/reference/test_coupled_dynamics.py`.

**Approach — convert both still-reproducing checks to tests, then delete the
harness.** Its remaining value is zero once they are items:

- The "mass balance cannot detect a wrong rate" half was addressed by PL-023
  (gate the coupled dynamics on an independent solution), whose RK4 oracle is
  the real answer to it.
- The step-size half is PL-VP7N.
- Its physics half is already
  `tests/reference/test_coupled_dynamics.py`, which supersedes it outright — an
  independent oracle that runs in CI beats a script somebody has to remember to
  invoke.

So: confirm each still-reproducing check has a test or an item standing in for
it, port anything that does not, delete `tools/review-verification/`, and clear
any citation of it from the documentation. Deleting it is the recommendation
rather than a fait accompli — it is reversible from git history, and the
alternative (wiring it into `make check`) would mean maintaining a second
verification path for checks the reference suite already makes.

**Done when.** Every still-reproducing harness finding is either a test in
`tests/` or an open queue item, `tools/review-verification/` is deleted, and no
document cites a path inside it.

**Resolved 2026-08-30.** Both scripts were run against the tree before
deleting anything, and the live picture had moved since this item was written.

All six `P1` defect checks report `FIXED`, each against a closed item. `P2-1`
no longer reproduces at all: it *raises*, because PL-VP7N's applicability-domain
guard now refuses the 10 s step the check itself constructs, so its step-size
half is closed in code and its mass-balance half is closed by PL-023's
independent RK4 oracle. The three physics checks (`P2-2`, `P2-3`, `ARCH`)
report `CONFIRMED`. `P2-4` is the only check that still reproduces, at -55.5%
/ -34.5% / -17.2% at 30 / 60 / 120 s, and PL-024 (document what the venous
pool does to early mixed-venous readings) already stands for it.

So the last live finding was not `P2-1` but `ARCH` - the demonstration that a
single matrix exponential is exact where the pairwise split is not - which had
neither a test nor an item. It is now PL-6GS0 (decide whether the coupled step
should be an exact matrix exponential rather than an operator split), carrying
the measured per-agent table so retiring the harness loses no evidence. An
item rather than a test, deliberately: a test of an exponential the shipped
code does not use would be a second solver maintained forever and gating
nothing, which is the duplicate verification path this item exists to avoid.

`tools/review-verification/` is deleted. Citations cleared from
`docs/ARCHITECTURE.md` (package-map tree and both prose references),
`ROADMAP.md`, `docs/WORKING_NOTES.md` (the thread rewritten around what is
still open), `tools/doc_check.py`'s `covered_dirs` comment, and
`tests/reference/test_coupled_dynamics.py`'s provenance docstring. Two open
gate items named files inside it and were re-measured rather than left
pointing at deleted paths: PL-020 (bring tests and `tools/` under the
type-check gate), whose entire `tools/` cost was this harness and is now zero,
and PL-69J3 (clear the inert `noqa` directives), which loses three of its ten
sites.
