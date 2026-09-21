---
id: PL-ZM8P
title: "doc_check's check_quoted_sources reads every item file while check_line_citations reads only live ones, so a closed brief quoting the Current baseline heading fails make check at the next release cut"
priority: P2
effort: S
status: done
classes: defect
feature: dev-tooling
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-21
closed: 2026-09-21
payoff: a release cut stops being blocked by drift the project has already decided is not a finding, and the two citation checks stop disagreeing about the same file
verify: uv run pytest tests/unit/test_doc_check.py -q -k "closed_brief or open_brief"
---

**Problem.** `tools/doc_check.py` has two checks that read citations out of
item briefs, and they drew opposite lines. `check_line_citations` goes through
`_live_item_briefs`, which skips `done` and `dropped` items because
`.claude/rules/citation-drift.md` records the ratified decision that **a closed
brief is a historical record, not a live assertion** and its drift is
explicitly not a finding. `check_quoted_sources` went through
`_quoting_sources`, which globbed `docs/items/*.md` and read every brief, open
or closed.

## Why it surfaced at a release cut, and why it would have recurred

`ROADMAP.md`'s `## Current baseline` section is **replaced wholesale at every
release** - v0.4.35's prose is not retained anywhere in the file, and neither
is v0.5.0's. So every heading inside it is guaranteed to disappear at the next
cut, and any brief quoting one goes red at that moment.

Cutting v0.5.1 hit exactly that: two errors, both in `PL-DL4M`, which is `done`
and closed *in this very release*:

```text
docs/items/PL-DL4M-...md:76: quotes ROADMAP.md as "Current baseline: v0.5.0", which is not in that file
docs/items/PL-DL4M-...md:93: quotes ROADMAP.md as "The branch reproduces its parent, asserted element-wise", which is not in that file
```

Neither is a defect in `PL-DL4M`. It quoted headings, which is the anchor
`.claude/rules/citation-drift.md` *prefers* over a line number, and those
headings were correct when it was written.

**The two ways out without this fix were both wrong.** Repairing the closed
brief falsifies the record - it would make a 2026-09-21 item cite prose that
did not exist when the work was done - and it is the hand-repair loop
`PL-38PN` → `PL-JXVD` already showed does not terminate. Editing `ROADMAP.md`
to preserve a heading a check wants distorts a standing document to suit a
tool. The defect was in the tool.

## The fix

`_quoting_sources` now yields `_live_item_briefs(root)` rather than globbing
the item directory, so both checks draw the same line from the same helper,
whose docstring already carries the reasoning. It is the only caller of
`_quoting_sources`, so nothing else moves.

**The exemption is narrow, and a second test holds it there.** Skipping closed
briefs is otherwise indistinguishable from switching the check off, so
`test_an_open_brief_quoting_a_deleted_heading_is_still_an_error` asserts the
live half still fires. The pair was proved to discriminate rather than merely
to pass: with the fix reverted, the closed-brief test fails and the open-brief
test still passes.

**Done when.** Both checks read live briefs only, the pair of tests is in
place, and `make check` is green. All three hold.
