---
id: PL-G21K
title: verify's suppression and assertion checks infer intent from diff text, so every fix adds a special case and uncovers the next: across 564 commits four of the five suppression markers fired zero times on a real directive while half of all hits were prose
priority: P2
effort: M
status: done
classes: defect, infra
feature: verify-false-reject
milestone: v0.5.0
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py, subprojects/docket/README.md
added: 2026-09-20
closed: 2026-09-20
pr: 797
payoff: retires the half of the suppression check that never once caught what it exists to catch - 33 of 33 real hits were legitimate type-ignores, none a disabled test - so a close-out touching verify.py stops REJECTing on the file's own docstrings, and the four items left behind it stop being patched one case at a time
verify: grep -q 'def test_a_type_ignore_is_not_a_suppression' subprojects/docket/tests/test_verify.py
root-cause-of: PL-4FD2, PL-STC4, PL-BHBZ, PL-5MFL, PL-XQGH, PL-CNJH, PL-2DTK
misread: Whether a branch's diff weakens its tests: a disabled test, or an assertion removed or loosened
---

**Problem.** `verify.py`'s two integrity checks — "no suppression added" and
"no existing assertion removed" — answer an *intent* question ("did this
session weaken the gate it was measured by?") with a *text* matcher over a raw
diff. Intent is the judgment half. Every fix so far has been a new special case
in the matcher, and each one has uncovered the next false positive, because the
question is not decidable at the layer it is being asked.

**Why it matters.** Both checks are absolute under `--self`, so every false
positive blocks a correct close-out until a reader talks past it - and a reader
who has learned to explain away this block is the reader who skims a real
protected-path finding. The inflow is the other half: seven open items, each a
session's diagnosis of one more case the matcher cannot see, and the next fix
uncovers the next case.

**Why this is a generator rather than seven defects.** The module docstring
already states the correct rule, and states it about itself: *"What it
deliberately does not do is decide whether the work is right … a tool that
implied otherwise would be worse than no tool."* `SUPPRESSIONS`' own comment
draws the line again, for `noqa`: *"Whether a `noqa` matters is a question for
the linter's own `RUF100`, not for a substring search, and answering it here
would be guessing at the judgment half."* Both checks then cross that line for
every other marker. `CLAUDE.md`'s "Do not script the judgment" is the same rule
a third time.

**The accretion, in order.** Assertion check: `PL-7TYC` (shape and file suffix),
`PL-K1WS` (pair a removal with its replacement), `PL-K82G` (the `falsifies:`
escape hatch), `PL-QJQL` (`with pytest.raises(...)`), `PL-XMNC` (replay scope),
`PL-K4R5` (name the candidates it cannot decide) — six fixes, and `PL-XQGH`,
`PL-CNJH` and `PL-2DTK` remain open. Suppression check: `PL-VHVJ`
(word-anchoring) — one fix, and it immediately produced four open items, three
of which are the same defect filed independently.

**The count, run 2026-09-20 over 564 commits on `main` since 2026-09-01.**
`_SUPPRESSION_RE` flags 66 added lines:

| what the flagged line is | lines | share |
| --- | --- | --- |
| `.md` prose — structurally incapable of holding a suppression | 22 | 33.3% |
| `.py`, marker only inside backticks, a string literal or a prose comment | 11 | 16.7% |
| `.py`, a directive that survives stripping both | 33 | 50.0% |

And the breakdown of those 33 is the finding:

| marker | real directives in 564 commits |
| --- | --- |
| `# type: ignore` | 33 |
| `typing.no_type_check` | 0 |
| `xfail` | 0 |
| `pytest.skip` | 0 |
| `@skip` | 0 |

All 33 are `# type: ignore[<code>]` with an explicit error code, all in a test
file, none in `src/`. The commonest are `[arg-type]` (19), `[assignment]` (5)
and `[method-assign]` (4) — the Qt monkeypatching shims. **Not one is a test
being disabled**, which is the thing the check exists to catch.

So the check's yield is: half its output is noise, and the other half is a
question that belongs to mypy. That is `CLAUDE.md`'s retirement test met on the
nose — *"a check that fires every run without changing a decision is a defect in
the check — it costs attention forever and trains a session to skim the output
where a real advisory also appears"* — with the aggravating detail that this is
one of the four checks `--self` may not relax, so every hit blocks a close-out
until a reader talks past it. `PL-K82G` refused exactly that outcome by name
when it built `falsifies:`.

**What would make this wrong, stated before the recommendation.** The
zero counts could mean the check is *deterring* `xfail` and `pytest.skip`
rather than that nobody writes them. That reading is not falsifiable from this
data and should not be dismissed. Two things weigh against it: a deterrent
that has never fired in 564 commits is paying its false-positive cost against
a hazard with no observed base rate, and the deterrence argument would license
keeping any check forever. The honest resolution is to keep the markers that
name a *disabled test* (`xfail`, `pytest.skip`, `@skip`, `typing.no_type_check`)
— they cost nothing, since they never fire — and to stop treating
`# type: ignore` as a suppression here, because it is the only one that does
fire and it is the one a tool can actually decide. `PL-CMCB` records that
`tests/` sits outside the mypy gate, which is why `warn_unused_ignores` cannot
answer it today; that, not a regex, is the repair.

**Three candidate resolutions, for the design round.**

1. **Drop `# type: ignore` from `SUPPRESSIONS`, and change nothing else.**
   The four remaining markers keep the check honest at zero observed cost.
2. **Narrow the matcher to code.** Strip backticks and string literals before
   matching, and apply the `.py` restriction the sibling check already carries.
   `PL-5MFL`, `PL-BHBZ`, `PL-STC4`, `PL-4FD2` and `PL-0KQP` each propose a piece
   of this; together they remove 33 of 66 hits and leave all 33 type-ignore hits
   untouched. Necessary, not sufficient.
3. **Retire the suppression check outright.** Defensible on the count, and the
   most likely to be wrong if the deterrence reading holds.

**Recommendation: 1 and 2, which are independent. Not a mypy change.**

**Widening mypy to `tests/` was considered here and is refused, because the
project already decided it.** `PL-CMCB` closed on 2026-09-01 (`v0.2.8`, pull
request 168) having asked exactly this question, and its **Approach** is a
standing decision rather than an oversight: *"Do not start by widening `files`
to include `tests`. The comment above `files` records the measurement that
argues against it ... and that comment is the standing decision."* Re-measured
2026-09-20 and it holds, harder than when it was written: `uv run mypy tests
subprojects/docket/tests` reports **427 errors in 63 files** under the project's
`strict = true`, and **255 errors in 37 files** even with `strict` off and only
`warn_unused_ignores` on - because `warn_unused_ignores` has to type-check a
file to know whether an ignore is load-bearing, so there is no cheap subset. Of
the 427, 201 are `[arg-type]`, which is what a test tree that deliberately
passes invalid inputs to validation code is *supposed* to contain.

**So dropping the marker loses no coverage that exists.** In `src/`, `tools/`,
`.claude/hooks/` and `subprojects/docket/src/` - everything in `[tool.mypy]
files` - `strict = true` already enables `--warn-unused-ignores`, so a
type-ignore there is policed by the tool that can actually decide it, and this
check adds nothing. In `tests/`, nobody polices it *by decision*, and a regex
that fires on all 33 is not a substitute for the checker that was declined: it
cannot tell a load-bearing ignore from an inert one, which is the only question
worth asking about one. Zero of the 33 observed hits were outside a test file.

**Done when** the suppression check's markers each have a recorded reason to be
there that its own `noqa` comment would accept, and the seven items above are
closed or dropped against it rather than patched one at a time.

**Not a licence to skip the instance fixes.** `PL-5MFL` is in flight and its
`.md` narrowing is free and correct — a Markdown file suppresses nothing. This
item is about the altitude the *next* six are worked at.

**Decision (project owner, 2026-09-20, ratified, over retiring the suppression
check outright and over any change to the mypy configuration).** Take
resolutions 1 and 2 together, which are independent:

1. **Drop `# type: ignore` from `SUPPRESSIONS`.** It is the only marker that
   fired on a real directive across 564 commits - 33 of 33 - and not one of
   those was a disabled test, which is what the check exists to catch. Where
   mypy already reaches, everything under `[tool.mypy] files`, `strict = true`
   enables `--warn-unused-ignores` and the check adds nothing. In `tests/` the
   marker goes unpoliced, and that is the accepted cost rather than an
   oversight.
2. **Strip non-code context before matching.** A marker inside backticks, a
   string literal, or a prose comment is not a suppression.

**Resolution 3 was refused** on the ground the item itself states: it is the
one most likely to be wrong if the deterrence reading holds, and the zero
counts cannot falsify that reading. The four never-firing markers stay, at
zero observed cost.

**No mypy change, and the phrasing above is corrected here.** The
`**Decision needed.**` block this replaces offered resolution 1 as "route
`# type: ignore` to mypy", which reads as a configuration change. It is not
what the body recommends and not what was decided: nothing under
`[tool.mypy]` moves. Widening `files` to `tests/` stays refused by
`PL-CMCB`'s standing decision, re-measured 2026-09-20 at 427 errors under
`strict` and 255 with `strict` off and only `warn_unused_ignores`.

**What pull request 783 already landed, so this item does not redo it.**
`PL-5MFL`, `PL-BHBZ`, `PL-4FD2` and `PL-0KQP` closed on 2026-09-20 with
`SUPPRESSION_BEARING_SUFFIXES` in `verify.py` - the *file-suffix* half of
resolution 2, which removes the 22 `.md` lines of the 66. What is left of
resolution 2 is the 11 `.py` lines whose marker sits inside backticks, a
string literal or a comment. `verify.py`'s own docstrings are in that set:
they name the tokens they match, so editing the file that defines the check
trips the check. That is why 783's own close-out REJECTed on 6 added lines,
none of them a suppression, and why it could not be cleared from inside that
branch.

## Worked 2026-09-20

**Both halves of the decision, in one change, because the first is what makes
the second decidable.** `# type: ignore` left `SUPPRESSIONS`, and a line's
quoted spans, backtick spans and trailing comment are blanked before matching
what is left, for `.py` and `.pyi`. `PL-STC4` had recorded the comment half as
undecidable and it was: a `# type: ignore` *is* a comment, so a rule that
ignores comments deletes the only marker that ever fired. With that marker gone
no entry is comment-shaped, and `test_no_suppression_marker_is_comment_shaped`
fails if one is put back - the coupling is silent otherwise, since
`SUPPRESSIONS` would name a marker the matcher could never see.

**Re-measured against the shipped module rather than a reimplementation**, by
importing `verify.py` from `HEAD` and from this branch and replaying every
added line of `main`. Over its 1,004 non-merge commits (1,121 including
merges, which carry no diff of their own):

| | lines |
| --- | --- |
| flagged by the check as it stood | 75 |
| flagged by the check as it now stands | 0 |
| newly flagged - matches the old check did not make | 0 |

Of the 75: **56 are real `# type: ignore` directives**, every one carrying an
explicit error code and not one of them a disabled test; the other **19 carry
their marker only inside a quote or backticks**. No marker but `# type:
ignore` has ever matched a real directive. Every one of the 75 is in a `.py`
file - no `.toml`, `.cfg` or `.ini` line has ever matched in either direction,
which is why the strip is applied to Python only, where a quote and a `#` mean
what this assumes. Replayed on `#783`'s own squash commit, the six lines that
`REJECT`ed it go to none.

**The item's `tests/` claim was out of date and the correction favours the
decision.** The brief says a dropped marker leaves `tests/` unpoliced as an
accepted cost. `tools/ignore_check.py` (`PL-J5NN`) has since run
`warn_unused_ignores` over `tests/` and `subprojects/docket/tests/` on every
`make check`, so all 56 are read by mypy: 11 inside `[tool.mypy] files` under
`strict`, 45 by that tool. What no tool polices is a *live* ignore added to
silence an error the work itself introduced - and neither did this check,
which flagged all 56 alike when all 56 were legitimate.

**A gap found while pinning the strip, filed rather than fixed: `PL-5B88`.**
`@pytest.mark.skip` and `@pytest.mark.skipif` match neither `@skip`, whose `@`
must sit against the name, nor `pytest.skip`, whose halves `.mark.` separates;
`@unittest.skip` matches nothing either. Measured on the module either side of
this edit, so it is standing rather than introduced. It matters twice: the
check reports `none` with a disabled test in the diff, which is the first
compounding-friction test; and it weakens the deterrence reading that kept the
check, since a deterrent that misses the common form deters less than the zero
count suggests. Widening `SUPPRESSIONS` is a different deliverable from the
one ratified here, so it is an item.

**What this decision did not reach.** The ratified decision and its three
candidate resolutions are about the suppression check. `PL-XQGH`, `PL-CNJH`
and `PL-2DTK` are the assertion check's, and nothing here re-scopes or drops
them: they stand as ordinary items. The altitude argument in the body applies
to them in the same words - six fixes so far, each uncovering the next - but
it has no ratified decision behind it, so a session picking the first of the
three should put one before working it rather than adding the seventh special
case.
