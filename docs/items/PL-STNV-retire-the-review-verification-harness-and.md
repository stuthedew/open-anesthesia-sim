---
id: PL-STNV
title: Retire the review-verification harness and capture its last live finding
priority: P2
effort: S
status: ready
classes: defect, infra
feature: dev-tooling
touches: tools/review-verification, tests/reference/test_coupled_dynamics.py, docs/WORKING_NOTES.md
added: 2026-08-30
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
