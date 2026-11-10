---
id: PL-7RLZ
title: Run a round's two meaning checks at the same time: tools/copy_edit.py runs every read and check one after another
priority: P2
effort: S
status: ready
classes: session-cost
feature: copy-editor
touches: tools/copy_edit.py, tests/unit/test_copy_edit.py
added: 2026-11-10
payoff: each round of the meaning check takes half the time, at the same cost and with the same verdicts
verify: grep -q 'def test_a_round_runs_its_meaning_checks_at_the_same_time' tests/unit/test_copy_edit.py
---

**Problem.** Run a round's two meaning checks at the same time: tools/copy_edit.py runs every read and check one after another

**Why it matters.** Each round of the meaning check runs the check twice
(`CHECK_PANEL` in `tools/copy_edit.py`) on the same edit, and the second run
does not use the first's result. The tool still runs them one after the
other, so a round takes twice the time it needs. A request can take five
rounds. Running the two at once changes no verdict and no token count. It
shortens the wait that the owner named on 2026-11-10.

**Done when.** The checks of one round run at the same time, the tool still
merges their replies as it does now, and a test in
`tests/unit/test_copy_edit.py` fails if they run one after the other.

**Generator check.** A one-off, found by reading the tool during the
owner's review of the copy editor on 2026-11-10.
