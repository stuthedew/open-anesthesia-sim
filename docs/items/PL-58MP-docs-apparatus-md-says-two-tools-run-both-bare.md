---
id: PL-58MP
title: docs/apparatus.md says two tools run both bare and under uv run, but quality.yml runs three (branch_id_check too), and README.md and CONTRIBUTING.md say make check runs everything CI runs, which doc_check's GATE_ONLY records is not so
priority: P3
effort: S
status: done
classes: docs
feature: one-source-of-truth
touches: README.md, CONTRIBUTING.md, docs/apparatus.md
added: 2026-10-19
closed: 2026-10-25
pr: 1760
payoff: a contributor no longer reads a green make check as a promise that CI will pass
verify: ! grep -qF 'everything CI runs' README.md CONTRIBUTING.md && ! grep -qF 'and two' docs/apparatus.md
reenters: PL-ZQ3R
---

**Problem.** docs/apparatus.md says two tools run both bare and under uv run, but quality.yml runs three (branch_id_check too), and README.md and CONTRIBUTING.md say make check runs everything CI runs, which doc_check's GATE_ONLY records is not so

**Why it matters.** A reader who trusts "`make check` runs everything CI runs" will treat a green local run as a green pull request. `tools/doc_check.py`'s `GATE_ONLY` records the checks that run in only one of the two gates, so that sentence is false, and the cost is a red CI run the reader did not expect. The `docs/apparatus.md` count is smaller: it says two tools run both bare and under `uv run`, and `.github/workflows/quality.yml` runs three that way: the two the document names, and `branch_id_check.py`.

**Done when.** `README.md` and `CONTRIBUTING.md` say that `make check` runs CI's checks except the ones `GATE_ONLY` lists, and point at that list rather than restating it. `docs/apparatus.md` gives the right count of tools run both ways, or points at the workflow instead of counting.

**Checked 2026-10-24.** `README.md` line 172 and `CONTRIBUTING.md` line 36 both say "everything CI runs". `quality.yml` runs `tools/branch_id_check.py` bare and again as `uv run python tools/branch_id_check.py`, and `docs/apparatus.md` still says "two more both bare and under it".

**Generator check.** A re-entry of `PL-ZQ3R`, closed 2026-10-18. The misread fact is "the checks the local gate and the merge gate each run, and where the two sets differ". `PL-ZQ3R`'s head states that fact, and its fix made `GATE_ONLY` the record. These two documents still restate the old claim of parity.
