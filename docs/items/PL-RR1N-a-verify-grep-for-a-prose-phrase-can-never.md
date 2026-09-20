---
id: PL-RR1N
title: A verify: grep for a prose phrase can never match once the document's own line-wrapping splits it, and exit 1 reads as work-not-done
status: untriaged
added: 2026-09-20
---

**Problem.** A verify: grep for a prose phrase can never match once the document's own line-wrapping splits it, and exit 1 reads as work-not-done

`grep` matches within a line. A `verify:` of the shape
`grep -qF '<phrase>' <doc>` therefore fails for as long as the phrase the
item's work adds is split across two lines by the document's own wrapping —
which markdown prose at this project's 79-column convention does to any phrase
longer than a few words, and which the author cannot see from the command.

**Why it matters.** The failure is not silent, but it is *misleading in the one
direction that costs most*: exit 1 is exactly what an unstarted item returns, so
a session whose work is complete and correct reads its own `verify:` as saying
the work is absent. Measured on `PL-FG9D` 2026-09-20: the command
`grep -qF 'contributes exactly two rates and one volume to the breathing circuit'`
returned 1 against a document containing that phrase, because the author's own
sentence wrapped after "and". The repair was to **restructure the prose so the
phrase fit one line**, which is the check dictating the document's wording
rather than measuring it.

The surface is large rather than incidental: 199 open items carry a `grep -qF`
command, and `.claude/skills/docket/SKILL.md` recommends exactly this shape for
a documentation-only item — correctly, since it is the one command whose exit
status stays readable. Nothing warns that the target must fit on one line.

**It does not meet `CLAUDE.md`'s compounding-friction bar**, which is why this
is filed rather than raised: it fails loudly rather than passing while its
guarantee is void, and it sits on `verify:` rather than on the store or the
gate. It is ordinary queued work.

**What the fix might be**, in rough order of preference — a fix is not settled
here:

- A `tools/` helper (standard library, no virtualenv) that normalises runs of
  whitespace before matching, so a command reads the document the way a reader
  does rather than the way a line does. `docket set` could then rewrite a bare
  `grep -qF` into it, which makes the fix retroactive for the 199.
- `bin/docket set` warning at write time when the phrase does not occur on any
  single line of an existing target file — cheap, decidable, and it fires at
  the moment the command is composed.
- A line in the skill telling authors to pick a phrase short enough to survive
  wrapping. Weakest: it is advice at the moment of writing, and the wrap can be
  introduced later by an unrelated edit to the surrounding sentence.

**Done when.** A `verify:` command written against a phrase in a wrapped
paragraph resolves correctly, or the author is told at write time that it will
not.
