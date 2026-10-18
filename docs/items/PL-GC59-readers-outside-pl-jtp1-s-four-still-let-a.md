---
id: PL-GC59
title: Readers outside PL-JTP1's four still let a caller drop a decline by writing nothing or an empty list: docket.shell's Reading.refusal and roadmap's MilestoneSection.unread, Scope and Wave.unread carry theirs as a record field, and doc_check's workflow_commands and workflow_runs take a list a caller can pass empty
priority: P3
effort: S
status: done
classes: refactor
feature: reader-checks
touches: tools/doc_check.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-17 triage pass
added: 2026-10-17
closed: 2026-10-18
payoff: doc_check's workflow readers hand back what they declined to read, so no caller can drop it by passing an empty list
verify: grep -q 'def test_workflow_commands_returns_its_declines' tests/unit/test_doc_check.py
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

**Why it matters.** A caller that passes `[]` to `workflow_commands`,
`workflow_runs` or `_step_scripts` silently drops what they declined to read,
and `tools/dead_ends.py` once dropped declines in exactly that way (`PL-DQ9C`).
Then a check reports a partial reading as a whole one.

**Decided at triage, 2026-10-17.** The brief's recommendation is taken. Only the
second half is work: `doc_check.py`'s readers return their declines beside their
result. The record-field half is closed as not worth its code, because a pair
refuses nothing that a field read does not, and every reader of the record
would need an edit. Reopen it only if a sweep finds a caller dropping a field's
declines.

**Done when.** `workflow_commands`, `workflow_runs` and `_step_scripts` return
their declines beside their result, take no list from the caller, and a test
pins that the declines are returned.

**Generator check.** Not a re-entry. `PL-JTP1` named its four readers on
purpose, and these are the readers it left. The fact is "a shared reader's
declines reach every caller", and no head records it.

**Closed 2026-10-18.** `workflow_commands`, `workflow_runs`,
`pull_request_runs` and `_step_scripts` return `(result, declines)` and take no
list. `pull_request_runs` had the same shape and was changed with them. The
rewritten assertions in `tests/unit/test_doc_check.py` keep their asserted
values; one, which compared the old bare list, now compares the pair.
