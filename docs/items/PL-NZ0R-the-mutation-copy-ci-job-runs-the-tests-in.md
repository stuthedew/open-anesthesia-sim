---
id: PL-NZ0R
title: The mutation-copy CI job runs the tests in mutmut's copy without mutmut's own pytest plugin, so a fault in that plugin stops every mutation run while the job passes, as PL-LR03's did for a day
priority: P2
effort: S
status: ready
classes: defect
feature: tests-detect-wrong-values
touches: .github/workflows/quality.yml, tools/diff_mutation.py
deferred-from: v0.7.0 - present at the freeze, not safety or science, and no user sees a wrong value from it: a broken mutation run stops a close-out with an error rather than passing it, and the release waits only on the owner's test drive (triage 2026-11-28)
added: 2026-11-28
filed-pr: 2346
payoff: a pytest or mutmut upgrade that breaks mutation runs fails the pull request that brings it, instead of stopping every close-out after it merges
---

**Problem.** The mutation-copy CI job runs the tests in mutmut's copy without mutmut's own pytest plugin, so a fault in that plugin stops every mutation run while the job passes, as PL-LR03's did for a day

**Why it matters.** `bin/docket verify --self` runs a mutation check at every close-out of simulator code, and it rejects a branch when the check gives no answer. On 2026-11-27 a pytest upgrade broke mutmut's own pytest plugin (`PL-LR03`). Every mutation run then stopped before its first mutant, and for about a day no close-out could pass. All that time the `mutation-copy` job, whose purpose is to catch a broken mutation run before it reaches `main`, passed on every pull request. The plugin is the part that a pytest or mutmut upgrade reaches, and it is the part the job leaves out.

**Reproduced 2026-11-28.** The `mutation-copy` job in `.github/workflows/quality.yml` runs only `uv run --locked --group mutation python tools/diff_mutation.py --first-step`. The docstring of `first_step` in `tools/diff_mutation.py` says that it leaves out mutmut's record of which functions each test calls, which took about 19 minutes on 2026-11-11, and that a fault in the plugin that keeps the record passes there.

**Approach.** In the same job, run the plugin's record over a small fixed set of tests, enough to pass through each of its hooks, such as `pytest_runtest_teardown`. One test file takes seconds, where the full record takes 19 minutes. Running the full record only on a pull request that changes pytest or mutmut in `uv.lock` was weighed and is weaker: it misses a plugin fault from any other cause, such as a change to `pyproject.toml`'s `[tool.mutmut]`.

**Done when.** The `mutation-copy` job runs mutmut's pytest plugin over at least one test, so that a fault like `PL-LR03`'s fails the job. The job takes no more than one minute longer than it did on 2026-11-28, and the run that shows both is written in this brief.

**Generator check.** A one-off. The job leaves the plugin out on purpose, to save time, and nothing else runs the plugin before a close-out does. No head's `misread:` names what a passing CI job proves about the step it stands in for.
