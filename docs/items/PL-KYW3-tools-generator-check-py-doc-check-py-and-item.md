---
id: PL-KYW3
title: tools/generator_check.py, doc_check.py and item_reads.py each restate the item-id grammar, all three more loosely than store.ID_PATTERN, so a tool and docket check disagree about what is an id
priority: P2
effort: S
status: ready
classes: defect, infra
feature: one-id-grammar
touches: tools/generator_check.py, tools/doc_check.py, tools/item_reads.py, tools/dead_ends.py, tools/pr_body_check.py, tools/fixture_id_check.py, tests/unit/test_generator_check.py, tests/unit/test_doc_check.py, tests/unit/test_dead_ends.py, tests/unit/test_pr_body_check.py, tests/unit/test_fixture_id_check.py, tests/unit/test_item_reads.py
added: 2026-09-21
payoff: every tool judges an id by the grammar `bin/docket check` enforces, so a session cannot be told an item is cited 6 times when 7 is the answer, and a sixth tool cannot restate the grammar without the build saying so
verify: uv run python tools/fixture_id_check.py && grep -q 'def test_a_restated_grammar_is_refused' tests/unit/test_fixture_id_check.py
---

**Problem.** tools/generator_check.py, doc_check.py and item_reads.py each restate the item-id grammar, all three more loosely than store.ID_PATTERN, so a tool and docket check disagree about what is an id

**Two more, found on the sweep.** `tools/dead_ends.py` (`PL-[A-Z0-9]{3,4}`) and
`tools/pr_body_check.py` (`PL-[0-9A-Z]{3,4}`) carry the same restatement and are
not in the title. Six sites across five files, so `touches` is widened rather
than the two left to be re-found: the feature is `one-id-grammar`, and closing
it with two tools still disagreeing would record a guarantee that does not hold.

**What the drift actually cost, measured 2026-09-21 against the store as it
stands (1,485 items, 43 of them historical three-digit ids).** The damage runs
in both directions and the two are not symmetrical:

- **Too tight on length.** The four sites spelled `{4}` cannot see a three-digit
  id at all. `generator_check.citations` was blind to **219 citation edges** to
  real open items, `creation_parents` could not read **44 item filenames** or the
  **6 creation-commit subjects** that lead with one. On today's tree the printed
  answer for the `docs/MODEL.md` cluster was `6 cited by 3+ open items`; the
  answer is 7. That is the apparatus floor's own failure - a confident answer
  that is wrong - in the tool a session reads to decide what a generator is.
- **Too loose on the alphabet.** All six admit the vowels `store.ID_ALPHABET`
  excludes, so `PL-AAAA`, `PL-STUV`, `PL-DONE` and nine more tokens in the tree
  read as ids. Harmless where the result is intersected with the store
  (`generator_check.citations`, `item_reads`), live where it is not
  (`dead_ends.check`, `pr_body_check.item_ids`).

**Fix.** Each tool inserts `subprojects/docket/src` on `sys.path` and imports
`ID_PATTERN` from `docket.store`, which is what `doc_check.py`,
`branch_id_check.py`, `pr_title_check.py` and `fixture_id_check.py` already do;
`tests/unit/test_tools_portability.py` already lists `docket` as the one
importable non-stdlib package, so nothing about the bare-checkout promise moves.
The pattern is interpolated bare, the way `docket`'s own `vcs.py`, `roadmap.py`,
`release.py` and `notes.py` interpolate it - no extra `\b` on either side, since
a boundary the store's own readers do not apply is a smaller version of the same
disagreement.

**And a guard, so there is no seventh site.** `tools/fixture_id_check.py` gains a
second rule: a `PL-` followed by a character class closed by a *counted*
quantifier is a second copy of `store.ID_LENGTH` and is refused, with the
`not-an-id` marker as the escape hatch. The counted quantifier is what makes it
exact - an open-ended `PL-[A-Za-z0-9]+` claims to know nothing about the grammar
and is left alone, which is why the check needs no exemption anywhere in the
tree today. Verified both ways: it names all eight occurrences across the six
pre-fix sites, and reports nothing on the repaired tree.

**Done when.** The six sites import the grammar; `fixture_id_check.py` refuses a
seventh; each tool's own test pins the historical three-digit id it could not
previously read.
