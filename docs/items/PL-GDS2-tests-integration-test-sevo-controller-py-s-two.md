---
id: PL-GDS2
title: tests/integration/test_sevo_controller.py's two replay tests are still named for the recorded history PL-2FM6 deleted, while comparing run_segments and the snapshot
priority: P3
effort: S
status: ready
classes: test, docs
feature: numerical-domain
touches: tests/integration/test_sevo_controller.py
added: 2026-09-14
verify: ! grep -qE 'def test_.*recorded_histor|def test_.*replay' tests/integration/test_sevo_controller.py && uv run pytest tests/integration/test_sevo_controller.py
---

**Problem.** tests/integration/test_sevo_controller.py's two replay tests are still named for the recorded history PL-2FM6 deleted, while comparing run_segments and the snapshot

**Why it matters.** A test's name is what a reader trusts when deciding whether
a failure matters, and these two name a thing `PL-2FM6` deleted: there is no
recorded history to replay, and what they actually compare is `run_segments`
against the snapshot. The cost is paid at the worst moment - a session reading a
red `test_..._replay` looks for a replay path that does not exist before it
looks at the comparison that failed. `CLAUDE.md` treats stale documentation as a
safety issue for this reason, and a test name is documentation a session reads
before the code.

**Done when.** Both tests are named for what they compare rather than for the
deleted recording, their docstrings say the same, and
`uv run pytest tests/integration/test_sevo_controller.py` still passes.
