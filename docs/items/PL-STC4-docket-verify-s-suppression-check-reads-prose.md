---
id: PL-STC4
title: docket verify's suppression check reads prose, unlike the assertion check beside it: 12 of the 13 lines it flagged on PL-VHVJ's own branch were an item brief, a comment or a docstring naming the thing being fixed
status: untriaged
added: 2026-09-19
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
