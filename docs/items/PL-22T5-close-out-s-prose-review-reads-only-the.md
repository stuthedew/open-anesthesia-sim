---
id: PL-22T5
title: Close-out's prose review reads only the paragraphs a branch changed and caps each rewrite at the old paragraph's length, so it cannot fold new text into the unchanged paragraph beside it and sets no cap on a new paragraph; PL-ZDZ0's three rounds took its MAC passage from 381 to 366 words, while a rewrite of the whole passage reached 260 with every value kept
status: untriaged
feature: reader-first-prose
touches: tools/new_prose.py, docs/prose-review/prompt.md, .claude/skills/docket/modes/close-out.md, .claude/rules/plain-writing.md
added: 2026-11-03
---

**Problem.** Close-out step 8 gives the reviewer each paragraph of 30 words or more that the branch changed, and nothing else. It asks for a rewrite no longer than the text it replaces. Three things follow.

1. The reviewer cannot see that a new paragraph repeats, or belongs inside, an unchanged paragraph beside it.
2. The length cap is the old paragraph, so a padded paragraph sets its own ceiling. A new paragraph has no cap at all.
3. `.claude/rules/plain-writing.md` says rewriting sentences a branch did not need to touch is work for its own item. So a fix adds a paragraph to a section and never merges it into what is there. Only a separate prose item ever shortens a section.

**Measured 2026-11-03.** The passage of `docs/MODEL.md` § "Displayed precision" from "The MAC resolution is derived from this one" to "silently over-claiming" was 381 words on `main`. `PL-ZDZ0` corrected one false sentence in it, and three prose-review rounds and the owner's request to shorten it brought it to 366 words at `ecf15dff6`. A rewrite of the whole passage, ordered for the clinician with the derivation and tests in a developer note, came to 260 words. It kept every value, unit and test, and passed `tools/doc_check.py` and `tools/literal_home_check.py` unchanged.

**Recommended.** Change the review's unit from the changed paragraph to the passage it sits in: from the heading above to the next heading, with the changed paragraphs marked. Ask for the shortest version of that passage that keeps every fact, ordered for its first reader. Allow the branch to rewrite that passage, and only that passage, even where its sentences did not need to change. Report the passage's word count before and after in the pull request. A passage that grows says what the added words buy.

**Cost.** Diffs on fix branches get larger, and a safety-tagged fix that waits on the owner's review gives them more to read. Limiting the licence to the passage the fix is in keeps that to a few paragraphs.

**Done when.** `tools/new_prose.py` prints each changed passage whole with its changed paragraphs marked, the prompt asks for the shortest passage, close-out step 8 states the passage licence and the word-count report, and the plain-writing rule's sentence about rewriting sentences you did not need to touch names the exception.

**Generator check.** Not counted. The open `prose-quality` rewrite items (`PL-J37P`, `PL-BSYT`, `PL-PS5H`, `PL-XBJ3`, `PL-XT53`, `PL-YVL0`, `PL-9331`) are each a section that fix branches grew and could not shrink, which fits this mechanism, but nobody has checked each one's history.
