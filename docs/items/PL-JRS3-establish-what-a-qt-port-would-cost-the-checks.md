---
id: PL-JRS3
title: Establish what a Qt port would cost the checks that read theme.py: contrast_check and agent_identity_check would pass silently on a tree they no longer describe
priority: P2
effort: S
status: ready
classes: defect, ux
feature: presentation-safety
touches: tools/contrast_check.py, tools/agent_identity_check.py, docs/ARCHITECTURE.md
verify: uv run pytest tests/unit/test_contrast_check.py tests/unit/test_agent_identity_check.py && grep -q 'PL-JRS3' tools/contrast_check.py
added: 2026-09-08
---

**Problem.** Establish what a Qt port would cost the checks that read theme.py: contrast_check and agent_identity_check would pass silently on a tree they no longer describe

**Problem, restated.** `tools/contrast_check.py` and
`tools/agent_identity_check.py` both read `src/anesthesia_sim/app/theme.py` and
the Flet control tree around it. They are the two checks standing between this
project and a chart no colour-blind reader can separate — `PL-JX0Z` and the
Brettel projection are what they enforce — and they are wired to a specific
toolkit's constants.

**Why it matters, and why it is filed now rather than during a port.** A Qt
port would leave both checks reading a `theme.py` that no longer describes what
is drawn. They would not fail; they would **pass**, on a tree they no longer
describe, which is exactly the failure mode `PL-20PT` had just been fixed for
and the one `CLAUDE.md` names as a check giving a wrong answer silently. A
port's own test suite would be green while the accessibility floor this project
argued for went unenforced.

This is not an argument against a port. It is the cost of one, and it is
cheaper to know it before `PL-QXSB` is decided than to discover it after
`PL-55DH` looks promising.

**Done when** it is established what each check actually depends on, and
whether the dependency is on the *values* — which survive any toolkit — or on
Flet's control objects, which do not. If the former, say so and the port is
cheaper than it looks. If the latter, the two checks are part of the port's
scope rather than collateral, and `PL-QXSB`'s cost side gains an entry.
