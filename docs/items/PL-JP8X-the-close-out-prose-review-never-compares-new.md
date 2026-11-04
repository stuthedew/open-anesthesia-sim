---
id: PL-JP8X
title: The close-out prose review never compares new text with the text it replaced in the document, so a branch can double a passage's length and pass: on PL-ZDZ0 the owner rejected the rewrite of a 163-word Displayed-precision passage three times as too long (first at about 210 words) before a 100-word version, and no review round flagged the length
priority: P1
effort: S
status: done
classes: defect
feature: reader-first-prose
touches: tools/new_prose.py, tests/unit/test_new_prose.py, tools/model_rewrite.py, tests/unit/test_model_rewrite.py, .claude/skills/docket/modes/close-out.md, docs/apparatus.md, docs/maintainer.md, docs/items/PL-22T5-close-out-s-prose-review-reads-only-the.md
deferred-from: v0.7.0 - captured after the freeze, and not safety or science; classed by the 2026-11-04 triage pass
added: 2026-11-03
closed: 2026-11-04
pr: 2014
payoff: a passage that doubled, or lost a value, a test name or an item id, is named before the owner reads it
verify: grep -q 'def test_a_passage_that_grew_and_lost_a_number_is_reported' tests/unit/test_new_prose.py
---

**Problem.** The close-out prose review never compares new text with the text it replaced in the document, so a branch can double a passage's length and pass: on PL-ZDZ0 the owner rejected the rewrite of a 163-word Displayed-precision passage three times as too long (first at about 210 words) before a 100-word version, and no review round flagged the length

**Why it matters.** Without the comparison, nothing tells the writer or the reviewer that a passage doubled. The owner is then the only check on length, and on `PL-ZDZ0` that took three rounds of their review.

**Decided under `PL-J1ZM`, 2026-11-04.** This is the decidable half of `PL-J1ZM` parts 2 and 4; `PL-22T5` builds the copy-editor agent that reads its output. The prototype run in `PL-J1ZM`'s brief also showed that a copy editor applying edits by default can drop a fact: it removed "above zero" from a display condition, and turned a "no test yet (`PL-19W8`)" declaration into "are untested". So the same script lists what an edit removed.

**Done when.** `tools/new_prose.py` prints, for each changed passage, its word count on the base and on the branch, and lists every number, name in backticks, item id and "no test yet" form that is on the base and not on the branch. A test in `tests/unit/test_new_prose.py` feeds it a passage that lost a number and grew, and finds both reported.

**Built, 2026-11-04.** `tools/new_prose.py --compare` prints each changed passage with its words on the default branch and now, then each file's lost facts. Close-out step 8 runs it after the rewrites, and says to name in the pull request the facts a grown passage's added words carry. Two choices were made in building it, both reversible:

1. **A passage is a run of changed paragraphs, not a section.** Each `-U0` hunk is widened to the paragraphs, table rows, docstrings or comments it reaches on both sides. Hunks parted only by blank lines are one passage. A section was the first design, but § "Displayed precision" of `docs/MODEL.md` is 8,095 words with no subheading, so a 47-word growth would not show. On #1992 the run reports the MAC passage as "163 words on main, 55 now", the 163 this item's title names.
2. **Lost facts are counted per file, through `tools/model_rewrite.py`'s `facts`.** That is the one grammar of a fact here, so a fact moved to the note for developers prints nothing, and one moved to an item is marked `moved`. The "no test yet" form was missing from it. It read as a bare item id, which that tool counts as history removed on purpose, so it is now a fact of its own and `lost` reports it too.

**Generator check.** Part of `PL-J1ZM`'s fix, not a new head: the fact misread is the one `PL-J1ZM` states, what a reader can do without.
