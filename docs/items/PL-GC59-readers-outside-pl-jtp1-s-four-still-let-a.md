---
id: PL-GC59
title: Readers outside PL-JTP1's four still let a caller drop a decline by writing nothing or an empty list: docket.shell's Reading.refusal and roadmap's MilestoneSection.unread, Scope and Wave.unread carry theirs as a record field, and doc_check's workflow_commands and workflow_runs take a list a caller can pass empty
status: untriaged
feature: reader-checks
added: 2026-10-17
---

**Problem.** Readers outside PL-JTP1's four still let a caller drop a decline by writing nothing or an empty list: docket.shell's Reading.refusal and roadmap's MilestoneSection.unread, Scope and Wave.unread carry theirs as a record field, and doc_check's workflow_commands and workflow_runs take a list a caller can pass empty

**Found 2026-10-17** by `PL-JTP1`'s build (`#1475`), which made the list
walker, `release.notes_bullets`, `frontmatter.statements` and
`model.parse_front_matter` return their declines beside their result, and
`release.unreferenced_by_version` too, so a caller that unpacks the result
holds the declines and the strict `mypy` run refuses one that unpacks fewer.
It read two other shapes and left them, since neither was among the readers
`PL-JTP1`'s plan named:

- **A record field.** `shell.Reading.refusal` (`PL-7CQ5`), and
  `roadmap.MilestoneSection.unread`, `Scope`'s and `Wave.unread` (`PL-L4X3`),
  are fields of a record with many readers. A reader of the record's other
  fields skips the decline by writing nothing, which no type refuses.
- **A list the caller passes.** `tools/doc_check.py`'s `workflow_commands(text,
  unread=None)` raises where no list is passed, and `workflow_runs(text,
  steps)` and `_step_scripts` take one, so `[]` drops what they decline: the
  shape `tools/dead_ends.py` dropped the walker's through (`PL-DQ9C`). Every
  caller in the tree passes its own list today.

**Recommendation.** Do the second half: return the declines beside the
commands as the walker does, which costs `tests/unit/test_doc_check.py`'s
assertions that list the commands (`verify --self` reads each rewritten one as
removed). Leave the first: a pair forces only a caller that unpacks it, and
`result[0]` skips the declines as quietly as a field read does, so turning a
record read in many places into a pair costs every reader an edit and refuses
nothing a field does not. Close that half as not worth its code unless a sweep
finds a caller dropping one.
