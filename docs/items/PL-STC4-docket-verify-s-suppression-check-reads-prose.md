---
id: PL-STC4
title: docket verify's suppression check reads prose, unlike the assertion check beside it: 12 of the 13 lines it flagged on PL-VHVJ's own branch were an item brief, a comment or a docstring naming the thing being fixed
priority: P2
effort: M
status: ready
classes: defect, infra
feature: verify-false-reject
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py
added: 2026-09-19
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
