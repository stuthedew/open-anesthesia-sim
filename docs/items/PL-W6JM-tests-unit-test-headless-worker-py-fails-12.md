---
id: PL-W6JM
title: tests/unit/test_headless_worker.py fails 12 tests when the checkout is shallow, as a cloud session's clone starts, because headless_worker clones with the checkout as a reference repository and git refuses a shallow reference (seen in make check on 2026-11-03)
priority: P2
effort: S
status: done
classes: defect
feature: api-credit-runs
touches: tools/headless_worker.py, tests/unit/test_headless_worker.py
deferred-from: v0.7.0 - captured after the freeze, and not safety or science; classed by the 2026-11-04 triage pass
added: 2026-11-03
closed: 2026-11-04
pr: 2021
payoff: make check passes in a shallow cloud checkout, and a worker run started from one makes its clone
verify: grep -q 'def test_a_shallow_checkout_clones_without_a_reference' tests/unit/test_headless_worker.py
---

**Problem.** tests/unit/test_headless_worker.py fails 12 tests when the checkout is shallow, as a cloud session's clone starts, because headless_worker clones with the checkout as a reference repository and git refuses a shallow reference (seen in make check on 2026-11-03)

**Reproduced 2026-11-04.** In a `git clone --depth 1` of this repository, `uv run pytest tests/unit/test_headless_worker.py` gave 12 failed and 29 passed. The first failure is `prepare_clone` in `tools/headless_worker.py`: "fatal: reference repository '.../.git' is shallow". The full checkout passes.

**Why it matters.** `make check` fails in any shallow checkout, so a session reads a red gate that its own change did not cause. A real worker run from a shallow checkout fails the same way, because `prepare_clone` borrows objects from the checkout it runs in.

**Done when.** `prepare_clone` clones without `--reference` when the checkout is shallow, and a test runs it from a shallow checkout and finds the clone made.

**Generator check.** Re-entry of `PL-KKX4`'s fact, what clone a session's checkout is and how much history it holds. `PL-KKX4` was dropped with its generator recorded spent, so it shipped no fix this could re-enter, and no `reenters` is recorded. One instance does not make the fact live again.

**Fixed 2026-11-04.** `prepare_clone` now passes `--reference` only where `docket.vcs.is_shallow` returns `False`, so a shallow checkout, or one git cannot describe, clones from `origin` alone. Against the code before the fix, `uv run pytest -q tests/unit/test_headless_worker.py -k shallow` failed with "`git clone` exited 128: fatal: reference repository '.../shallow/.git' is shallow".

In a `git clone --depth 1 --no-single-branch` of the repository, one more test then failed: `test_the_delegable_list_is_read_without_the_bash_launcher`. Docket correctly gives no delegable list when it cannot compare every branch with the base on truncated history, and the runner refuses with it. The test now accepts that refusal only where git says the checkout is shallow. With both changes, all 42 tests in the file pass in that shallow clone.
