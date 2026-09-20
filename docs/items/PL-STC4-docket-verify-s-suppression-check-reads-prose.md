---
id: PL-STC4
title: docket verify's suppression check reads prose, unlike the assertion check beside it: 12 of the 13 lines it flagged on PL-VHVJ's own branch were an item brief, a comment or a docstring naming the thing being fixed
priority: P2
effort: M
status: done
classes: defect, infra
feature: verify-false-reject
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py
added: 2026-09-19
closed: 2026-09-20
pr: 797
verify: grep -q 'def test_a_suppression_named_in_an_item_brief_is_not_one' subprojects/docket/tests/test_verify.py
---

**Problem.** docket verify's suppression check reads prose, unlike the assertion check beside it: 12 of the 13 lines it flagged on PL-VHVJ's own branch were an item brief, a comment or a docstring naming the thing being fixed

**Where it comes from.** `PL-VHVJ`'s own close-out audit, 2026-09-19. That item
fixed a substring collision in `SUPPRESSIONS`; auditing the branch that fixed it
reported `FAIL  no suppression added - 13 line(s)`, and the breakdown is the
finding:

| where the flagged line was | lines |
| --- | --- |
| `docs/items/PL-VHVJ-….md` - the item's own brief | 7 |
| `verify.py` and `test_verify.py` comments and docstrings | 5 |
| a test fixture string that *is* an `@pytest.mark.xfail`, as the subject under test | 1 |

None of the thirteen suppresses anything. An item whose subject is the
suppression detector cannot have a brief that does not name suppressions, so
this is not an unlucky wording — it is structural for any work on this check.

**The precedent is one check away, and already decided.** The removed-assertion
check beside it narrows twice for exactly this reason. `ASSERTION_BEARING_SUFFIX
= ".py"` keeps it out of the documentation tree, on the stated ground that
"every close-out edits its own item's `.md`, and every release edits
`ROADMAP.md`, so the documentation tree is where a substring grep over the word
`assert` met a session most often". And `is_assertion_line` removes "a line that
merely contains the word" (`PL-7TYC`). The suppression check took neither
narrowing, and the same two would remove 12 of these 13.

**Why it matters rather than being cosmetic.** This is one of the four integrity
checks `--self` may not relax, which is precisely why its signal has to be
clean: a reader who has learned to explain away its block is the reader who
skims a real protected-path finding. `PL-69JZ` and `PL-7XTS` are the same
failure already paid for once, in the four guards that `--self` now reports
rather than refuses.

**What needs deciding, and it is the only hard part.** The `.md` narrowing is
free — a Markdown file suppresses nothing, and the analogous rule is already
written for its sibling. The comment and docstring half is not: a `# type:
ignore` *is* a comment, so "ignore comments" would delete the check's main
finding. Stripping a line's trailing comment before matching does not help
either, for the same reason. The honest split is probably that a line whose
suppression name sits inside backticks or inside a string literal is being
*discussed*, not applied — which is judgment enough that it wants a design
round rather than a patch.

**Done when** an item brief no longer counts as a suppression, and the comment
half is either narrowed on a rule that cannot swallow `# type: ignore` or
recorded as undecidable with the reason.

**A second item for this defect was captured independently, three minutes later.**
`PL-BHBZ` - "bin/docket verify's suppression check reads every added line
regardless of file type, so prose naming xfail in ROADMAP.md or a release note
REJECTs a correct close-out" - was filed on 2026-09-19 by the session cutting
v0.4.29, on `origin/claude/loving-hawking-fyyc98`, and names the same missing
narrowing: the `.py` restriction the sibling assertion check carries at
`verify.py:160` and the suppression check at `verify.py:1269` does not. It is
not in this checkout, so it is cited here by title rather than by a link a
checker can follow.

The two are worth keeping apart until both land, because they are the same
defect found from opposite ends and each carries evidence the other does not:
this item has the 13-line breakdown from `PL-VHVJ`'s own branch and the
argument that the comment half is not decidable, and `PL-BHBZ` has the
`ROADMAP.md`-and-release-note failure mode, which is the case that will fire on
every release. Whichever session lands second should fold `PL-BHBZ`'s evidence
into this brief and drop it with a `reason`, or the reverse - one item, not
two.

**It is also a live instance of `PL-TZ7T`**, the item this same triage pass
seated: `bin/docket new` files a duplicate title without noticing. Two sessions
running concurrently filed one defect twice inside four minutes - this pass's
triage commit at 19:39:47 UTC, `PL-BHBZ`'s capture at 19:43:03 - which is the
third recorded occurrence after `PL-LBR6`/`PL-5QLP`/`PL-QMC0`.

**Probable duplicate of `PL-4FD2`, found 2026-09-19 while grouping this item.**
`PL-4FD2` reads: "verify's suppression check greps every added line for the
three marker substrings it knows, so prose in a docstring, an item brief or a
README explaining why a suppression was not used refuses the branch." That is
this defect, described independently. Both are now in `verify-false-reject` so a
session meeting either sees the other. Whether they merge, or one is dropped
with a reason, is a decision for whoever works them — not something to settle
from the titles. This is also a live instance of `PL-TZ7T` (`bin/docket new`
files a duplicate title without noticing): two captures, one mechanism, filed
apart.

## Half of this landed in `#783`, 2026-09-20 — read this before starting

`PL-5MFL` and `PL-BHBZ` were worked together and closed in `#783`, by a
session that had not found this item or `PL-4FD2`. That is a fourth instance
of `PL-TZ7T` (`bin/docket new` files a duplicate title without noticing), and
it means **the file-suffix half of this item is done**. What follows is what
landed, so nobody pays for it again.

**Landed.** `is_suppression_line(path, line)` in
`subprojects/docket/src/docket/verify.py` now asks the path first, against
`SUPPRESSION_BEARING_SUFFIXES = (".py", ".pyi", ".toml", ".cfg", ".ini")`.
Deliberately wider than the sibling's `ASSERTION_BEARING_SUFFIX`: an assertion
is a statement, so only executed code holds one, while a suppression is also
*configured* - `xfail_strict = false` under `[tool.pytest.ini_options]` turns
every expected failure back into a pass with no Python changing. Three tests
pin it, including one holding the wider list against a later narrowing to
`.py` alone.

Counted before it was written, per `.claude/rules/expert-review.md`: across
1,109 commits the added lines the matcher finds are 69 `.py` and 41 `.md`,
**no other suffix carrying one at all**. Replayed on the real cuts, v0.4.30
(`fe32c6f`) went from 7 reported lines to 0.

So of this item's own 13-line breakdown above, the **7 item-brief lines are
gone**. The 5 comment-and-docstring lines and the 1 test fixture remain, and
they are the whole of what is left.

**Measured again on `#783`'s own branch**, which is the cleanest evidence this
item has because the branch was doing exactly this work: **6** added `.py`
lines reported, none a suppression - two docstrings naming `xfail_strict` to
explain the suffix list, three test fixtures that must write a literal marker
into a scratch repository, and one assertion pinning the tuple the check
reports. `PL-BHBZ`'s own "Done when" requires that a `.py` line containing a
marker still fails, so this REJECT is **structural for any work on this
check** rather than unlucky wording.

**Folded in from `PL-4FD2`** (dropped 2026-09-20 as the same defect; it read
"prose in a docstring, an item brief or a README explaining why a suppression
was not used refuses the branch"). Two things it carried that this item did
not:

- It was found closing `PL-Q9Z1`, where the refusing lines were a docstring
  paragraph, an item brief and a `README.md` paragraph - and that branch's
  workaround was to *avoid the word*, which makes the documentation worse in
  the one place a reader needs it, since the reason a suppression was refused
  is what stops the next session adding one.
- **The precedent for the remaining half is already in this tree**:
  `tools/doc_check.py`'s `candidates` reports a term that is also an ordinary
  word *only where a line marks it as code*. That is the same line this check
  still does not draw, drawn deterministically and shipping.

**Folded in from `PL-0KQP`** (dropped 2026-09-20, captured on `#783`'s branch
before its author found this item): a file-level `# type: ignore` on its own
line is a real mypy directive for the whole file, so "the line is a comment"
cannot be the predicate - which is this item's own decidability argument,
reached independently and with the concrete counter-example.

**A candidate rule the design round should weigh, found 2026-09-20.** This
item already names it - "a line whose suppression name sits inside backticks
or inside a string literal is being *discussed*, not applied" - but the
backtick half alone is decidable with no idea of Python's grammar, which is
what `verify.py`'s own `TOKEN_RE` comment warns against growing. A backtick is
never Python syntax outside a string or comment, and a real directive is never
written backticked. Scored against the evidence above: it clears 4 of `#783`'s
6 and the 5 comment-and-docstring lines of the 13. What it does **not** clear
is the test fixture that genuinely contains a marker as the subject under
test, which is honest reporting rather than a false positive. Not built, and
not this session's to decide.

**Still open, and unchanged:** whether to narrow within `.py` at all, and on
what rule. `docs/WORKING_NOTES.md:1987` records the decision that this item
goes ahead of product work.

## Superseded as the place the decision lives, 2026-09-20 — read this first

A generator item was recorded the same day and declares this item one of its
causes. It merged to `main` in `#787` as `PL-G21K`, so it is in the store and
citable directly - this paragraph was written while it was still stranded on
`origin/claude/busy-einstein-8bmtwd` and said it was not.

> `PL-G21K` — "verify's suppression and assertion checks infer intent from
> diff text, so every fix adds a special case and uncovers the next: across
> 564 commits four of the five suppression markers fired zero times on a real
> directive while half of all hits were prose". `status: needs-decision`,
> `feature: verify-false-reject`, and
> `root-cause-of: PL-4FD2, PL-STC4, PL-BHBZ, PL-5MFL, PL-XQGH, PL-CNJH, PL-2DTK`.

**Do not build this item's remaining half without reading it.** Its count over
564 commits of `main` splits `_SUPPRESSION_RE`'s 66 flagged lines three ways:
22 (33.3%) `.md` prose, 11 (16.7%) `.py` where the marker sits in backticks, a
string literal or a prose comment, and 33 (50.0%) real directives - **every one
of the 33 a `# type: ignore[<code>]` in a test file, and not one a test being
disabled**. `typing.no_type_check`, `xfail`, `pytest.skip` and `@skip` fired on
a real directive **zero** times.

Two consequences for this item:

- The 33.3% row is what `#783` landed, so that part is done rather than
  pending.
- The 16.7% row is this item's own backtick candidate, already measured. So
  the remaining half is not a patch this item should specify - on `PL-G21K`'s
  evidence the question is whether the check should be asking this at all, and
  that is a decision rather than a narrowing.

This item's value from here is its evidence, not its disposition: the 13-line
breakdown, the `PL-Q9Z1` finding folded from `PL-4FD2`, and
`tools/doc_check.py`'s `candidates` as the in-tree precedent. Whether it
closes as part of `PL-G21K` or survives it belongs to whoever answers
`PL-G21K`, not to this brief.

## Worked 2026-09-20, with `PL-G21K`

The comment half is narrowed on a rule that cannot swallow `# type: ignore`,
which is the disposition this item asked for and the one it could not reach
alone. `is_suppression_line` now blanks a `.py` or `.pyi` line's quoted spans,
backtick spans and trailing comment before matching; the rule is safe because
`PL-G21K` dropped `# type: ignore` from `SUPPRESSIONS` in the same change, so
no marker is comment-shaped, and a test fails if one is added back.

All thirteen of this item's own breakdown are now quiet: the seven item-brief
lines by `#783`'s suffix rule, and the five comment-and-docstring lines and the
one fixture string by the strip. Four tests pin them - an item brief, a
docstring reached by its backticks with its opening quotes on another line, a
prose comment, and a fixture string that *is* a `@pytest.mark.xfail` - beside
one that pins a real marker still reported when strings and a comment sit on
its line.

`PL-4FD2`, the probable duplicate named above, was dropped against `#783`. The
open question this item left - whether the comment half was decidable at all -
is answered by the coupling rather than by a better matcher.
