---
id: PL-MM7F
title: GitRunner memoizes a failed git call, so one non-zero exit is served to every later caller in the session and a transient failure becomes a permanent wrong answer
priority: P2
effort: S
status: done
classes: defect
feature: evidence-declines
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_git_runner.py, subprojects/docket/tests/test_vcs_silence.py
added: 2026-09-19
closed: 2026-09-19
verify: grep -q 'def test_a_call_git_did_not_answer_is_put_to_git_again' subprojects/docket/tests/test_git_runner.py
---

**Problem.** GitRunner memoizes a failed git call, so one non-zero exit is served to every later caller in the session and a transient failure becomes a permanent wrong answer

**Found in `PL-BHVM`'s design round, 2026-09-19**, which carries the wider
diagnosis. This is the amplifier rather than the defect: `PL-Q9Z1` is the
inverted failure direction, and this is what makes one instance of it permanent.

`GitRunner.__call__` in `subprojects/docket/src/docket/vcs.py` caches
unconditionally for every subcommand in `_READ_ONLY`:

```python
text = self._serve(argv, root)
...
if memoizable:
    self._memo[key] = text
```

`_serve` ends in `_run_git`, which collapses a non-zero exit, a missing git and
a timeout alike to `""`. So a failure is stored in the memo exactly as a real
answer would be, and every later caller asking the same question is served the
same silence without git being consulted again. `diff` is in `_READ_ONLY`, so
this covers the `diff --numstat` call `PL-Q9Z1` is about.

**Why it matters.** The memo exists so that 82 of 192 duplicate subprocesses
are paid once (`session-start-cost`). Caching a *failure* inverts that: one
transient fault — a ref deleted by another session between the `for-each-ref`
that lists it and the `diff` that reads it — is amortised across the whole
session instead of being retried. It also removes the one thing that would
otherwise make such a fault self-correcting, which is that the next caller asks
git again.

**Done when** a call whose git failed is not stored in the memo, and a test
drives a failing git twice against one `GitRunner` and asserts git was asked
both times. Depends on `PL-Q9Z1`: until `_run_git` can say a call failed,
nothing here can tell a failure from an empty answer worth caching.
