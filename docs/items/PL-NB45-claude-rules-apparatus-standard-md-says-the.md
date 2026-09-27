---
id: PL-NB45
title: .claude/rules/apparatus-standard.md says 'the fifteen apparatus tests under tests/unit/' where workflow_paths lists 35, and a count in a rule drifts at the rate tools/ grows
status: untriaged
touches: .claude/rules/apparatus-standard.md
added: 2026-09-27
---

**Problem.** .claude/rules/apparatus-standard.md says 'the fifteen apparatus tests under tests/unit/' where workflow_paths lists 35, and a count in a rule drifts at the rate tools/ grows

**Evidence, 2026-09-27.** Line 52 of `.claude/rules/apparatus-standard.md`:
"nothing stricter applies to the fifteen apparatus tests under `tests/unit/`".
`docket.toml`'s `workflow_paths` lists 35 such files, and
`tools/workflow_paths_check.py` counts the same 35 on the real tree. The
number was true when written and is wrong in the direction that undersells
the rule's reach.

**Recommendation:** drop the number - "the apparatus tests under
`tests/unit/`" - rather than update it, since `workflow_paths` and the check
already say which files those are and a count here is a third copy that
drifts at the rate `tools/` grows. Found by `PL-12P8`'s docs sweep; not fixed
there because the file is outside that item's `touches`.
