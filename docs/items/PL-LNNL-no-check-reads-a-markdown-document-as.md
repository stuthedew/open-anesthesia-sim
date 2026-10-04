---
id: PL-LNNL
title: No check reads a Markdown document as CommonMark does, so a prose wrap that puts a spaced hyphen or plus sign at a line start renders a clause as a list item unnoticed - PL-DSMK's four in ROADMAP.md, PL-N7LK's four and PL-T4FK's one - and a rule refusing it must tell those apart from the 31 lists that interrupt a paragraph on purpose
priority: P3
effort: M
status: blocked
classes: docs
feature: prose-renders-as-written
touches: tools/doc_check.py, tests/unit/test_doc_check.py
blocked-by: PL-R417
added: 2026-10-04
payoff: a prose wrap that would render a clause as a stray list item fails make check where it is written, instead of being found on the rendered page one capture at a time
---

**Problem.** No check reads a Markdown document as CommonMark does, so a prose wrap that puts a spaced hyphen or plus sign at a line start renders a clause as a list item unnoticed - PL-DSMK's four in ROADMAP.md, PL-N7LK's four and PL-T4FK's one - and a rule refusing it must tell those apart from the 31 lists that interrupt a paragraph on purpose

**Why it matters.** A wrapped marker is invisible in the raw text, which is
what every session reads, and plain on the rendered page, which is what the
owner and every outside reader see. So sessions that never see it write it,
and it is found only when somebody reads a page closely. `PL-DSMK` fixed four
in `ROADMAP.md` on 2026-10-04, one splitting a section citation so that no
reader could find it; `PL-N7LK` and `PL-T4FK` hold the five left that day, one
of them `docs/MODEL.md` crediting brain and liver with a 59.0% share of cardiac
output that belongs to four organs. Fixing lines one capture at a time leaves
the mechanism standing, and the next wrap is one reflow away.

**Measured 2026-10-04** by `PL-N7LK`'s triage, scanning every tracked Markdown
file outside `docs/items/` with markdown-it-py 4.2.0: 36 lists interrupt a
paragraph. Five are wrapped markers, the ones `PL-N7LK` and `PL-T4FK` hold, and
31 are lists by intent: 19 in `docs/pr-bodies/`, ten in the YAML front matter
of `.claude/rules/` files, and one each in `docs/worker.md` and
`docs/releases/v0.5.9.md`. A rule refusing every list that interrupts a
paragraph would fire 31 times on correct text, so it has to read the
difference, for instance whether the line above ends mid-sentence or
introduces a list, and that difference is measured against those 31 before it
is written down.

**Done when.** `python3 tools/doc_check.py check` fails, naming file and line,
on a list item that interrupts a paragraph where the text reads as a wrapped
clause, and passes the intended lists counted above; a test in
`tests/unit/test_doc_check.py` pins both halves. Standard library only, as
every tool here is, so the rule reads CommonMark's condition for a list
interrupting a paragraph itself rather than importing a Markdown parser.

**Held by the generator pause** (triage, 2026-10-04). A new check, which
`CLAUDE.md` § "What this project is" holds while any open item carries
`generator: live`, as the capturing session said in `PL-N7LK`'s title. On
`main` at `f71c7a64`, `bin/docket generators` marks `PL-R417` still
generating, its last slice open in #1353. Before promoting, check that
`bin/docket generators` marks no head "still generating"; building it sooner
is the owner's call, made by asking (`PL-6Q9L`).

**Generator check.** Not a member; the fix side of `PL-R417`'s fact for
writers. Its three instances, `PL-DSMK`, `PL-N7LK` and `PL-T4FK`, are recorded
as that head's in `PL-N7LK`'s brief. `PL-R417`'s own fix makes readers read a
continued statement whole, and reaches no writer, so this check is what would
stop the next instance.
