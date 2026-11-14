---
id: PL-RTYG
title: The merge-hold check runs on Python 3.11 and cannot parse a product test written for the project's Python 3.14, so it refuses a pull request the owner has approved: #2119 is held because tests/unit/test_new_prose.py uses a nested-quote f-string
priority: P1
effort: S
status: done
classes: defect
touches: .github/workflows/merge-hold.yml, tests/unit/test_tools_portability.py
deferred-from: v0.7.0 - a workflow defect found 2026-11-14, after the freeze; not safety or science
added: 2026-11-14
closed: 2026-11-14
pr: 2147
payoff: a pull request the owner approved is not held because the check cannot parse a product test
verify: grep -q 'python-version-file: .python-version' .github/workflows/merge-hold.yml
---

**Problem.** The merge-hold check runs on Python 3.11 and cannot parse a product test written for the project's Python 3.14, so it refuses a pull request the owner has approved: #2119 is held because tests/unit/test_new_prose.py uses a nested-quote f-string

**What happens.** `.github/workflows/merge-hold.yml` installs Python 3.11, the
floor `subprojects/docket/pyproject.toml` declares, and runs `bin/docket arm
--merge-hold`. For a changed test under `tests/`, `arming.py` parses both sides
with `ast` to learn whether the test imports `anesthesia_sim`. The product is
written for Python 3.14 (`.python-version`). Python 3.12 and later let an
f-string reuse its own quote inside a replacement field, and 3.11 cannot parse
that. `tests/unit/test_new_prose.py` does it on `main` (line 1107,
`f"{new_prose.rows_span('doc.md § "Part"', 1, 20)}:"`), so every branch that
changes that file gets `unknown` and exit 2 on 2026-11-14, whatever the
owner's read says. `#2119` was held this way after the owner approved it.

**Fix.** The merge-hold job parses the product's files, so it runs on the
product's interpreter: `python-version-file: .python-version`. The docket
floor is still proven by the floor section of `quality.yml`. The job reads the
workflow file from the default branch (`pull_request_target`), so the fix must
merge before a held pull request's check can pass.

**Why it matters.** The check that stops a merge refuses work the owner has
already approved, and the only way past it is a manual merge that bypasses
the gate.

**Done when.** The merge-hold job installs the interpreter `.python-version`
names, and a re-run of the check on `#2119` passes.

**Generator check.** One-off: one job running the floor interpreter on files
written for a newer one. `branch-sweep.yml` and `pr-title.yml` also run 3.11
but parse no product file.

**Fixed, 2026-11-14.** The job installs the interpreter `.python-version`
names. `test_the_merge_hold_job_runs_on_the_product_interpreter` in
`tests/unit/test_tools_portability.py` failed on the old workflow
(`assert 'python-version-file: .python-version' in ...`) and passes now.
