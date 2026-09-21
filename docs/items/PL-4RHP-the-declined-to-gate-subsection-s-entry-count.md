---
id: PL-4RHP
title: The Declined-to-Gate subsection's entry count is outside check_gate_counts' reach, and its group counts cannot be reconciled to the 151 it states
priority: P3
effort: S
status: done
classes: docs, defect
feature: debt-gate
touches: ROADMAP.md, tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-16
closed: 2026-09-21
pr: 839
verify: python3 tools/doc_check.py check && ! grep -qE '^#{2,6} .*entr(y|ies)[[:space:]]*$' ROADMAP.md
recurrences: 2026-09-19 PL-HCTF, 2026-09-21 PL-JN3F
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

**Why it matters.** It is a number in `ROADMAP.md` that reads as checked and is
not. `check_gate_counts` exists because "a count written into a document goes
stale the next time an item closes", and every other gate count in that document
is inside its reach - so a reader has no way to tell this one apart from the ones
the checker holds. That is the first of `CLAUDE.md`'s compounding-friction
shapes in miniature: the guarantee is void while the check reports correctly.

**It has moved again since this item was filed.** The heading read 151 entries on
2026-09-16 and reads **152** on 2026-09-17, which is the item's own prediction
arriving nine days early. Its history is now eleven hand edits.

**Done when** the heading states no count, and nothing in the subsection states
one either. Triage chose that remedy over reconciling the number and building a
check for it - which is what this item's `verify:` command pins - on `CLAUDE.md`'s
own grounds: the subsection's purpose is that each disposition is written down
with a reason, which no total carries, and a check built to hold a number nobody
reads would fire on every run without changing a decision. Reconciling instead
remains admissible if whoever takes it finds the count load-bearing somewhere
this reading missed; the command is then repointed, since the item is open.

**Confirmed 2026-09-19 by `PL-4FBP`'s ratified convention** (a live assertion names what it asserts, a dated one carries its date).
No change. The heading states no count, which is exactly what the counts rule
now requires, so triage's choice here *is* the rule rather than an instance
awaiting one.

**Swept 2026-09-19 under `PL-6ZQY` (crossing-lane consolidation): still real, with stale numbers corrected here rather than in the text above.** The heading still states a count
and no check reads it: `ROADMAP.md:2977` is
`### Declined to Gate 2 on the refilling-queue ground — 192 entries`, outside
`_subsection_end`'s range and unmatchable by `GATE_GROUP_RE`, which requires a
line opening `*` or `**`. The count has kept moving since the brief recorded
151 then 152 - `git log -L 2977,2977:ROADMAP.md` shows 174 → 175 → **192** in
the two most recent commits touching the file, which is the item's argument
running while nobody watches. Note that the brief's closing "The heading states
no count" is the end state being asked for, not a description of the tree.

**`PL-HCTF` is this same finding and is dropped in its favour** (`PL-JKML`'s
duplicate sweep, 2026-09-20). Filed 2026-09-19 against the same heading, the
same `check_gate_counts` gap and the same two candidate remedies, by a session
that could not see this item. It sat at `needs-decision` asking which remedy
governs - which triage here had already answered, and which `PL-HCTF`'s own
brief agrees is a session's call rather than the project owner's. So the store
held an open decision whose answer was already recorded two items away. Its
evidence is stronger than this brief's and is carried here:

- **The proof that nothing reads the number, measured 2026-09-19.** `python3
  tools/doc_check.py check` was run against one tree with the heading reading
  `174 entries`, `191 entries` and `999 entries` in turn. All three report
  `0 errors, 0 advisories`. That is a sharper demonstration than this brief's
  own 151 → 150 edit, because 999 is not a plausible drift.
- **The drift has a named instance.** `#706` (`PL-ZMGR`) added a declined entry
  to the subsection on 2026-09-19 and left the heading at `174`. Nothing said
  so, and the session that wrote it had no way to be told. `PL-2P9L` then added
  seventeen and bumped to `191`, which preserves the off-by-one rather than
  repairing it - so the true total has been one higher than the stated one
  since `#706`, whatever the heading currently says.
- **Why the count cannot simply be checked as written.** "Entry" here is not
  "id mentioned": the subsection names ids for context as well as for
  disposition, so a naive count returns **324** against a heading of 191. Any
  check holding the heading to the entries below has to sum the batch sizes the
  paragraphs state ("Eleven more", "Fourteen more", "One more") instead. That
  is what makes remedy 1 more expensive than it looks, and it is the reason
  triage chose remedy 2.
- **Not `PL-0VFF`**, which is that the list does not distinguish a still-open
  declined entry from a closed one. This item is the stated total, and it is
  wrong before the open/closed question is asked.

**The reconciliation is part of this item either way.** Removing the number
from the heading disposes of the drift going forward; `origin/main`'s existing
off-by-one is disposed of by the same edit, since a heading that states no
count cannot be wrong by one.

**Closed 2026-09-21 on the remedy triage chose, with a check behind it.** The
heading states no count, and neither does any other heading in the gate's
section: `ROADMAP.md`'s `### Declined to Gate 2, because this milestone's own
work created them`, `### Deferred to v0.4.26, because the port dissolves the
defect` and `### Sequenced past v0.5.0, so not clearable before it begins`
carried the same unreadable number for the same reason, and the rule is pitched
at the position rather than at the word "Declined" - two of the tree's four
counted headings are worded otherwise, so the narrower rule would have been
falsified by the tree it was written against.

`tools/doc_check.py`'s `_uncheckable_heading_counts` refuses an entry count in
any heading below the `##` of a section that records a gate, and
`check_gate_counts` reports each as an error naming the line and the number.
This is not the check triage refused: that one would have *held* the number,
firing on a document nobody had broken and needing "entry" to be counted
against a subsection that records some entries as prose and some as bullets
(128 bullets against a heading of 228, with the first thirty in prose). This
one asks whether a heading states a count at all, which is decidable, and is
silent on a clean tree. `docs/MODEL.md` § "Counts, which both halves meet"
already stated the rule for prose - "stated only where a check holds it to what
it counts … or it is dated" - and a heading can carry no date, so it has no
third option.

The reconciliation the brief left open is disposed of rather than performed:
the subsection's own body says twice that its count is deliberately not written
down (`ROADMAP.md`'s `PL-0VFF` paragraph, and the closing "How many
dispositions this section holds is deliberately not written down"), so the
edit makes the document consistent with itself. Prose counts are untouched and
are `PL-DHJ7`'s (about thirty-five bold count paragraphs in the live sections),
which this neither closes nor blocks.

