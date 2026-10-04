---
id: PL-MFVV
title: docket's roadmap list walker (list_entry_lines, under list_entries) ends an entry at an unindented line CommonMark reads as that entry's lazy continuation (0.31.2 section 5.2), so a Required-scope or gate entry wrapped without an indent is read short and its declaration lost; doc_check's _list_members declines the shape by name since PL-R417 slice 1, the walker's other readers do not
priority: P3
effort: M
status: done
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/roadmap.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests, subprojects/docket/README.md, tools/doc_check.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
closed: 2026-10-04
pr: 1343
payoff: a frozen-list or Required-scope entry continued without an indent is refused by name - by make check, wave and the digest - instead of read short with nothing saying so
verify: grep -q 'def test_the_walker_declines_a_lazy_continuation_by_name' subprojects/docket/tests/test_roadmap.py && grep -qF '"frozen list, a lazy continuation is refused"' tests/unit/test_doc_check.py
---

**Problem.** docket's roadmap list walker (list_entry_lines, under list_entries) ends an entry at an unindented line CommonMark reads as that entry's lazy continuation (0.31.2 section 5.2), so a Required-scope or gate entry wrapped without an indent is read short and its declaration lost; doc_check's _list_members declines the shape by name since PL-R417 slice 1, the walker's other readers do not

**Found by** `PL-R417` slice 1 (`#1332`), which taught `doc_check`'s
`_list_members` to decline the shape by name and left the walker's own readers
in `docket.roadmap`, `_gate_entries` and `_scope_entries`, as they were: outside
that slice. A member of `PL-R417`'s head. Measured 2026-10-04: three lazy lines
follow list entries in `ROADMAP.md` (lines 2636, 2680 and 3989, the document
defects `PL-DSMK` holds). One, line 2636, follows a gate entry docket reads:
`PL-V6M0`'s, in v0.5.0's frozen list. There the walker's reading happens to be
the author's - the bold paragraph is separate prose that lost its blank line -
and the entry's leading id is read either way, so nothing is misread today and
the fault is latent. The head's fix applies: the walker reports a lazy line itself,
so every reader of it declines by name from one place rather than one reader
at a time. `PL-DSMK`'s blank line before line 2636 has to land first, or that
refusal fires on v0.5.0's list. `docket new` matched this capture to `PL-W9BK` on the shared path
alone; that item is about which entries `wave` counts as blocked outside the
gate, and this is not it.

**Reproduced 2026-10-04**, on a roadmap of one milestone run through
`parse_milestones` on `main` at `45f8e9f3`. A `Required scope` entry
"1. **A displayed clinical unit**, named in a title long enough to wrap" over
an unindented "(queue item PL-MNPQ)." comes back as an entry declaring
nothing, while the subsection's joined text declares `PL-MNPQ`; and a gate
entry "- PL-BCDF **and**" over an unindented "PL-GHJK (S) ..." comes back
holding `PL-BCDF` alone. markdown-it-py 4.2.0 folds each unindented line into
its entry, as § 5.2 says. So the scope half fails loud and names the wrong
thing - `tools/doc_check.py` reports a declaration missing that is there - and
the gate half undercounts with nothing saying so.

**The fix.** The walker reports the line itself, so its three readers decline
from one place:

- `list_entry_lines` takes an `unread` list. At an unindented line CommonMark
  reads as the entry's lazy continuation it raises `UnreadEntry` - the line,
  and why - where its caller passes no list, and otherwise puts it there and
  ends the entry where it always has, so one doubtful line costs the reader
  nothing it could read.
- What makes a line lazy is `CONTINUED_LINE`, which moves here from
  `tools/doc_check.py` so both tools read paragraph continuation from one
  definition; docket cannot import `doc_check`, and `doc_check` already
  imports this module.
- `parse_milestones` passes a list for the frozen list and `Required scope`,
  and each `MilestoneSection` carries what was declined as `unread`.
  `doc_check` fails each one by line, `wave` says its plan rests on a list not
  read whole and exits 1, as it does for a timeline that does not parse, and
  the digest's plan line says so. Not through `problems`: a release cut
  refuses on those because a reservation might be unread, and a list entry
  holds no version.
- `doc_check`'s `_list_members` stops testing the line itself and declines
  through the walker, with the same words.

**Why it matters.** One reader declines the shape and two do not, which is the
recurrence `PL-R417` exists to end: a gate entry or a declaration wrapped
without an indent is read short, and the answer docket gives from it - the
gate's count, what the milestone places - is handed over as whole.

**Done when.** The walker reports an unindented lazy continuation itself,
raised or recorded; `MilestoneSection.unread` carries it for the frozen list
and `Required scope`; `doc_check` fails it by line, `wave` and the digest say
the plan was not read whole, and `_list_members` declines through the walker;
each pinned by a test, with a frozen-list and a `Required scope` case in
`PL-R417`'s guard, `CONTINUED_STATEMENTS`. `PL-DSMK`'s blank line lands first,
in its own commit, so v0.5.0's frozen list reads clean when the refusal does.

**Generator check.** A member of `PL-R417`, whose `root-cause-of` names it and
whose `misread:` states the fact: where one statement ends, in a format that
lets a statement continue across physical lines - here a Markdown list entry
continued by a lazy line. Not a re-entry of `PL-6SRZ`, closed in `#1332`, which
taught `doc_check`'s reader alone.

**Closed 2026-10-04**, in `#1343`. The walker declines as the fix above says,
through `UnreadEntry` and `MilestoneSection.unread`: `check_milestone_lists`
fails each line, `wave` prints them under a heading of their own and exits 1,
and the digest's plan line says so. Measured with the new walker, v0.5.0's
section declines two lines on `main` before `PL-DSMK` - 2636, and 2680, which
follows a wrapped dash the walker read as an entry under the same gate heading,
so "one" above undercounted - and none after it. Two refinements came with the
move, each checked with markdown-it-py 4.2.0: `CONTINUED_LINE` takes a thematic
break (`---`, `***`, `___`) as ending a paragraph rather than continuing it
(§ 4.1, § 4.3), and the walker's `LAZY_LINE_RE` takes a block quote's `>` as
interrupting one (§ 5.1). Without them `make check` would refuse a list
followed by either, which CommonMark reads as written.
