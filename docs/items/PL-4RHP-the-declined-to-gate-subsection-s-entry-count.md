---
id: PL-4RHP
title: The Declined-to-Gate subsection's entry count is outside check_gate_counts' reach, and its group counts cannot be reconciled to the 151 it states
status: untriaged
feature: debt-gate
added: 2026-09-16
---

**Problem.** The Declined-to-Gate subsection's entry count is outside check_gate_counts' reach, and its group counts cannot be reconciled to the 151 it states

**Problem.** `ROADMAP.md`'s `### Declined to Gate 2 on the refilling-queue
ground — 151 entries` states a count that no check reads. `check_gate_counts`
reads two things only: a group heading *inside* the frozen-list subsection, and
a version- or timeline-table cell naming the release. `_subsection_end` stops at
the first `###` after the gate heading, and `GATE_GROUP_RE` requires a line
opening with `*` or `**`, so this `###` heading is outside both. Verified by
editing 151 to 150 and re-running `python3 tools/doc_check.py check`: 0 errors,
unchanged.

**It is maintained by hand and it does move.** `git log -L` over the heading
shows nine changes, the last two on 2026-09-15: `d56f857` took it 151 → 152 and
`c8f8068` took it back to 151.

**What could not be reconciled.** Summing the subsection's bold group
openers - "These twenty-nine", "The thirtieth", then every "N more ..." -
gives 181, or 173 once the eight explicitly "disposed of here rather than added
to the list" are taken out. Neither is 151. Either several of those openers are
partitions of a group above rather than additions (the reading this session
could not settle from the prose), or the count has drifted since 2026-09-15.
This is exactly `check_gate_counts`' own stated reason for existing: "a count
written into a document goes stale the next time an item closes".

**What was *not* changed on this finding.** `PL-R7XK` moved `PL-MN4J` out of
this subsection and left the heading at 151, deliberately: its paragraph said it
was "written down with a reason rather than listed", and the commit that added
it (`05dec92`) did not bump the count. So it was never one of the 151 and moving
it out changes nothing. That is a separate question from whether 151 is right.

**Found 2026-09-16** while implementing `PL-R7XK`.

**Where.** `ROADMAP.md` § "Declined to Gate 2 on the refilling-queue ground";
`tools/doc_check.py` `check_gate_counts`, `_gate_groups`, `GATE_GROUP_RE`.

**Done when** either the count is reconciled to the subsection and a check holds
it there, or the heading stops stating a number. The second is cheaper and may
be right: `CLAUDE.md` says a count nobody can check is a count nobody is
checking, and the subsection's purpose is that each disposition is written down,
which no total carries.
