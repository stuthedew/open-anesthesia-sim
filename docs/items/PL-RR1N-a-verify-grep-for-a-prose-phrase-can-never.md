---
id: PL-RR1N
title: A verify: grep for a prose phrase can never match once the document's own line-wrapping splits it, and exit 1 reads as work-not-done
priority: P2
effort: M
status: ready
classes: defect
touches: subprojects/docket/src/docket, subprojects/docket/tests
added: 2026-09-20
payoff: stops a finished item's own verify: reporting the work as absent because the document wrapped the phrase it greps for
verify: grep -rq 'def test_a_verify_phrase_split_by_line_wrapping' subprojects/docket/tests tests/unit
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

**The 199 above is the wrong population, and the correction changes what the
fix is worth** (triage, 2026-09-20). Counted against the store that day: **198
items in total** carry a `grep -qF` command and **41 of them are open** (`ready`,
`blocked`, `needs-decision` or `untriaged`). 180 open items carry some
`grep -q` form. So the live surface is 41, not 199 - the original figure
counted the closed items too.

That matters for the third bullet above in particular. "`docket set` could then
rewrite a bare `grep -qF` into it, which makes the fix retroactive for the 199"
cannot be done for the other 157: `.claude/skills/docket/SKILL.md` makes a
closed item's `verify:` a record of what was run rather than a command that
still runs, and `docket check` errors on rewriting one. So a retroactive rewrite
reaches 41 items, and the argument for the helper has to stand on those.

The defect itself is unchanged and still reproduces - the `PL-FG9D` case is
dated and recorded above, and nothing about the count touches it.
