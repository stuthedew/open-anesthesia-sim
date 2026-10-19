---
id: PL-MZCN
title: tools/headless_worker.py records a failed run with no reason: it drops claude's stdout and stderr, so the owner's first real run printed 'error, $0.00' and nothing said why
priority: P2
effort: S
status: done
feature: api-credit-runs
touches: tools/headless_worker.py, tests/unit/test_headless_worker.py
added: 2026-10-19
closed: 2026-10-19
verify: uv run pytest -q tests/unit/test_headless_worker.py
---

**Problem.** tools/headless_worker.py records a failed run with no reason: it drops claude's stdout and stderr, so the owner's first real run printed 'error, $0.00' and nothing said why

**Found 2026-10-19, on the owner's first real run.** It printed
`PL-08SS on claude-opus-5-5: error, $0.00, not pushed`, and the runner had
thrown away Claude Code's output, so nothing said why. A cost of $0.00 means
the run failed before any model work: the key, the credit or the model name.

**Fixed.** Each run's full output is now saved beside its clone as
`<clone>.log`. A failed run records a `reason` in the ledger, taken from the
result's own message or the last line of stderr. The printed line adds
`why: <reason>` underneath. `tests/unit/test_headless_worker.py` runs a fake
`claude` that refuses with "Invalid API key" and checks all three.

**Generator check.** Not a head: the third defect in one new tool, found on its
first real use. All three are its own, with no shared mechanism elsewhere.
