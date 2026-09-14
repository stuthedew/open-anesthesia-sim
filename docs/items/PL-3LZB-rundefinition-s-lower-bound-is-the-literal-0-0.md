---
id: PL-3LZB
title: RunDefinition's lower bound is the literal 0.0 and _segment_index_at wraps, so any definition opening after zero would answer from its last segment instead of refusing
priority: P1
effort: S
status: done
classes: defect, safety
feature: scenario-branching
milestone: v0.4.25
touches: src/anesthesia_sim/core/run_definition.py, tests/unit/test_run_definition.py
added: 2026-09-14
closed: 2026-09-14
pr: 572
verify: uv run pytest tests/unit/test_run_definition.py && grep -q 'def test_a_run_definition_is_under_no_settings_before_it_opens' tests/unit/test_run_definition.py
---

**Problem.** RunDefinition's lower bound is the literal 0.0 and _segment_index_at wraps, so any definition opening after zero would answer from its last segment instead of refusing

**Where it is.** `RunDefinition._require_within_run` refuses `elapsed_s < 0.0`
against the literal `0.0` rather than against the first segment's opening, and
`_segment_index_at` returns `bisect_right(...) - 1`, which is `-1` for an
instant before the first opening and indexes the **last** segment in Python.

**Unreachable today, and silent if reached.** `__init__` opens the first
segment at `0.0` and the bound refuses anything below it, so no negative index
was produced across 460 public calls (measured 2026-09-14 while working
`PL-TFX5`, the case that holds a trunk and its branches). If a definition ever
opens after zero, the two combine into a wrong answer rather than a refusal:
`_propagator` returns `None` for a non-positive interval, so `state_at` hands
back the last segment's keyframe unchanged. Measured on a definition whose
segments open at 600 s and 900 s, `state_at(0.0)`, `state_at(100.0)` and
`state_at(599.9)` all returned 0.005664 alveolar fraction, and
`evaluate_anchored(0, 500, 100)` drew a *varying* curve - 0.005664, 0.005664,
0.005610, 0.005565, 0.005520, 0.005664 - across a span the run did not exist
for.

**The fix, and that it is free.** Move the lower bound to
`self._segments[0].opening.elapsed_s` and make `_segment_index_at` refuse a
negative index rather than wrap. Measured as a strict no-op on the current
tree: the whole suite passes with both patched in. Needs a regression test of
its own, since nothing on the tree can reach the wrap.

**Independent of `PL-ZMRT`** (whether a branch's definition should open at the
fork instant). That item's brief called this guard a blocking cost of answering
it yes; it is not, because it lands on its own. Answering `PL-ZMRT` yes makes
the wrap reachable, so this must be in place first - but it is worth landing
either way.
