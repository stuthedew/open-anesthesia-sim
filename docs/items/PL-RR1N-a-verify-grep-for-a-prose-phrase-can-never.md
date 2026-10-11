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

**Re-pointed 2026-09-23 at `PL-1P5V`'s admitted shapes, which do not fix this
but change where the fix goes.** A `grep -qF` for a phrase is the shape the list
prescribes, and wrapping still splits it. What changed is that a command may
now run nothing outside the list: this brief's first route, a `tools/` helper
that normalises whitespace, is a new program a command may not call until it
joins the list with its argument beside it in `checks.py`; the second, a
write-time warning, reads the parsed clause - pattern and paths - rather than a
shell line. Either way the fix is a new admitted shape or a check on the
admitted one, written beside `checks.verify_shape_refusal`.

## Next steps (2026-10-11, handed on unstarted)

Re-confirmed 2026-10-11 against the tree: the defect still holds - a literal
`grep` phrase that a document wraps across two lines is on no single line, so
the command reads as work not done. Claimed by the gate batch in `#1410`, which
stopped for length before starting it and yielded the claim; nothing is built.
The design worked out before the stop, for whoever picks it up:

- **Where.** Beside `checks.verify_shape_refusal` and `_grep_refusal`, as
  `PL-R417`'s spent decision names ("a check on the admitted grep shape,
  written beside checks.verify_shape_refusal"). `checks.py` is pure and imports
  `verify.py`, so the detector lives in `checks.py` and its inputs are gathered
  in `cli._analysis()`.
- **What it detects.** A literal grep clause - `-F`, or a pattern with no
  regex metacharacters - with `-i` folded and the path globs expanded, whose
  phrase is absent from every single line of the target but present once the
  lines are joined. Markdown joins through `docket.markdown.statement_lines`
  and `unmarked`, so list markers and quote prefixes do not break the join;
  other files join on whitespace with a shared `#`, `>` or `//` marker
  stripped. Negated clauses (`! grep -q`) count too, since a wrapped phrase
  makes them pass vacuously.
- **Wiring.** Through the verify replay (`LandedReport` and `already_passing`),
  so it reaches `check --verify` and `set --verify`'s replay, plus a diagnosis
  on `verify`'s failing command check naming the phrase and the line pair it
  straddles. An error, since the reading is exact.
- **First, measure.** Run the detector over the open items' `verify:` commands
  against the tree and repair any phrase already wrapped, declaring those item
  files in this item's `touches`.
- **Test.** `test_a_verify_phrase_split_by_line_wrapping...`, the name this
  item's own `verify:` greps for.
