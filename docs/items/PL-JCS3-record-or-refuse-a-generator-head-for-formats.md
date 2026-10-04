---
id: PL-JCS3
title: Record or refuse a generator head for formats whose statements span lines but are read one line at a time - PL-6P6H, PL-G2FY and PL-Z8RS after PL-Q9LK, all in tools/doc_check.py - a fact no head's misread: states, which the 2026-10-03 triage classed as one-offs and instances of existing heads
priority: P2
effort: S
status: done
classes: housekeeping
touches: docs/items
added: 2026-10-03
closed: 2026-10-04
pr: 1329
payoff: six readers' captures are ranked as one generator head instead of six one-offs, so its next member is stopped at the source
not-delegable: The deliverable is a judgment - whether six items misread one fact no head states - and a grep for the recorded fields would pass on a head recorded wrongly
---

**Problem.** Record or refuse a generator head for formats whose statements span lines but are read one line at a time - PL-6P6H, PL-G2FY and PL-Z8RS after PL-Q9LK, all in tools/doc_check.py - a fact no head's misread: states, which the 2026-10-03 triage classed as one-offs and instances of existing heads

**Found 2026-10-03**, answering the project owner's follow-up on preventing the
day's predictable failures. Four readers in `tools/doc_check.py` took a
physical line for the statement of the format they read: `PL-Q9LK` (done that
day: a workflow `run:` script's heredoc body and backslash continuations),
`PL-6P6H` (a folded `run: >` block), `PL-G2FY` (a Makefile recipe continued by
a backslash) and `PL-Z8RS` (a Markdown code span that wraps). Each format
defines one statement across several physical lines: YAML 1.2.2 § 6.5 "Line
Folding" and § 8.1.3 "Folded Style", GNU make's "Splitting Recipe Lines", POSIX
shell § 2.2.1 (backslash-newline) and § 2.7.4 (here-documents), and CommonMark
0.31.2 § 6.1, where a code span's line endings become spaces. The Python
Language Reference § 2.1 names the distinction - a logical line built from one
or more physical lines - and LangSec calls input-handling spread through the
processing code "shotgun parsing" (Momot, Bratus, Hallberg and Patterson, IEEE
SecDev 2016).

**The other reading.** The triage pass on pull request 1316 classed `PL-6P6H`
and `PL-G2FY` as one-offs, testing each against `PL-PVW2`'s and `PL-KGYT`'s fact
and as a re-entry of `PL-Q9LK`, and classed `PL-Z8RS` as an instance of
`PL-KGYT`'s fact. Both hold for what they test. This item asks the triage
rule's third question of the four together - one fact misread by two or more
items, which no head's `misread:` states - and `bin/docket generators
--misread` listed no head about lines on 2026-10-03. `PL-Q9LK` and `PL-Z8RS`
can misread both facts.

**Candidate fix, if a head is recorded:** each reader recognizes its format's
continuation forms and declines a line it cannot place, rather than reading a
fragment as a statement - `.claude/rules/apparatus-standard.md`'s "say what it
could not read", applied where the line is read. One logical-line reader per
format is the larger version of the same fix.

**Done when.** A head is recorded with `root-cause-of:`, `generator:` and
`misread:`, or this brief records why the four are one-offs after all.

**Why it matters.** An unrecorded generator ranks nowhere. Each member was
triaged on its own, and each fix taught one reader one format's continuation
rule while the next reader went on taking a physical line for a statement:
`PL-Q9LK`'s own fix filed two of the three that followed it.

**Recorded 2026-10-04: a head, `PL-R417`.** One fact misread by six items, and
no head's `misread:` states it: where one statement ends, in a format that lets
a statement continue across physical lines. The six are the four named above
and two older ones a store search for line-at-a-time readers found:
`PL-6SRZ` (`check_named_tests` cannot match a backticked test name a wrap
breaks, filed 2026-09-21) and `PL-RR1N` (a `verify:` grep cannot match a phrase
the document's wrapping splits, filed 2026-09-20). `bin/docket show PL-Q9LK`
already printed its three refilings as the generator threshold.

- **The other reading holds for what it tested, and does not decide this.**
  "Not two spellings disagreeing" was asked of `PL-PVW2`'s and `PL-KGYT`'s
  fact; these readers misread a third. `PL-Q9LK` and `PL-Z8RS` have both
  causes - a second spelling, wrong because its format continues a statement -
  so each stays in its first head too, and `PL-74T0` records that its cluster
  1 count stands.
- **Not `PL-9HD1`'s, though it is the earlier instance.** Its fact is the item
  front matter's grammar, one format of this family, and its third member
  (`PL-V6CR`, quoting) is not about lines, so its `misread:` stays as written
  and `PL-R417` names it.
- **Live, not spent**: six filings in fifteen days, three of them on
  2026-10-03 alone, and `PL-R417` lists the readers still taking a physical
  line in `tools/doc_check.py` that no item names yet.

**Generator check.** Work the project owner asked for: the recording step for
one candidate head, and a member of no cluster.
