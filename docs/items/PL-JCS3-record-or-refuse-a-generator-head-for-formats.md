---
id: PL-JCS3
title: Record or refuse a generator head for formats whose statements span lines but are read one line at a time - PL-6P6H, PL-G2FY and PL-Z8RS after PL-Q9LK, all in tools/doc_check.py - a fact no head's misread: states, which the 2026-10-03 triage classed as one-offs and instances of existing heads
status: untriaged
added: 2026-10-03
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
