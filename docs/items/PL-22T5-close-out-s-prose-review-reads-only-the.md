---
id: PL-22T5
title: Close-out's prose review reads only the paragraphs a branch changed and caps each rewrite at the old paragraph's length, so it cannot fold new text into the unchanged paragraph beside it and sets no cap on a new paragraph; PL-ZDZ0's three rounds took its MAC passage from 381 to 366 words, while a rewrite of the whole passage reached 260 with every value kept
priority: P1
effort: M
status: ready
classes: defect
feature: reader-first-prose
touches: tools/new_prose.py, docs/prose-review/prompt.md, .claude/skills/docket/modes/close-out.md, .claude/rules/plain-writing.md, .claude/agents/copy-editor.md, docs/prose-review
deferred-from: v0.7.0 - captured after the freeze, and not safety or science; classed by the 2026-11-04 triage pass
added: 2026-11-03
payoff: a fix branch can shorten the passage it touches, and every cut arrives with its reason, so sections stop growing between rewrites
verify: grep -rqF --include=copy-editor.md 'name: copy-editor' .claude/agents
---

**Problem.** Close-out step 8 gives the reviewer each paragraph of 30 words or more that the branch changed, and nothing else. It asks for a rewrite no longer than the text it replaces. Three things follow.

1. The reviewer cannot see that a new paragraph repeats, or belongs inside, an unchanged paragraph beside it.
2. The length cap is the old paragraph, so a padded paragraph sets its own ceiling. A new paragraph has no cap at all.
3. `.claude/rules/plain-writing.md` says rewriting sentences a branch did not need to touch is work for its own item. So a fix adds a paragraph to a section and never merges it into what is there. Only a separate prose item ever shortens a section.

**Measured 2026-11-03.** The passage of `docs/MODEL.md` § "Displayed precision" from "The MAC resolution is derived from this one" to "silently over-claiming" was 381 words on `main`. `PL-ZDZ0` corrected one false sentence in it, and three prose-review rounds and the owner's request to shorten it brought it to 366 words at `ecf15dff6`. A rewrite of the whole passage, ordered for the clinician with the derivation and tests in a developer note, came to 260 words. It kept every value, unit and test, and passed `tools/doc_check.py` and `tools/literal_home_check.py` unchanged.

**Recommended.** Change the review's unit from the changed paragraph to the passage it sits in: from the heading above to the next heading, with the changed paragraphs marked. Ask for the shortest version of that passage that keeps every fact, ordered for its first reader. Allow the branch to rewrite that passage, and only that passage, even where its sentences did not need to change. Report the passage's word count before and after in the pull request. A passage that grows says what the added words buy.

**Why it matters.** A fix branch can only add to a section, so each section grows until a separate rewrite item shortens it. The clinician reading `docs/MODEL.md` gets the point later in each round, and the seven open `prose-quality` rewrites are the cost so far.

**Cost.** Diffs on fix branches get larger, and a safety-tagged fix that waits on the owner's review gives them more to read. Limiting the licence to the passage the fix is in keeps that to a few paragraphs.

[superseded 2026-11-04: PL-J1ZM's design round replaced the prose review with a copy-editor agent; the Done-when below is the decided form] **Done when.** `tools/new_prose.py` prints each changed passage whole with its changed paragraphs marked, the prompt asks for the shortest passage, close-out step 8 states the passage licence and the word-count report, and the plain-writing rule's sentence about rewriting sentences you did not need to touch names the exception.

**Decided under `PL-J1ZM`, 2026-11-04.** The owner ratified `PL-J1ZM`'s four-part design, and this item is its parts 2 and 3: a copy-editor agent replaces the close-out prose review, and reads whole passages from heading to heading. `PL-JP8X` is the script half, the before-and-after comparison in `tools/new_prose.py`. Build `PL-W8FL` and `PL-43GT` first, per `PL-J1ZM`'s build order.

**Done when** (2026-11-04, decided form). `.claude/agents/copy-editor.md` exists, starts without the resident instructions, and holds the review prompt that now lives in `docs/prose-review/prompt.md`. It reads each changed passage whole, from the heading above to the next heading, with the changed paragraphs marked. It cuts only for one of the three reasons in `PL-J1ZM` part 2 and returns each cut with its reason. Close-out step 8 runs it on every branch, its edits apply by default, and the writer reverts one only where it lost or changed a value, unit, condition, identifier or citation. The pull request title and body, and any reply to the owner that is a decision request or runs over 150 words, go through it as `PL-J1ZM` part 3 says. `.claude/rules/plain-writing.md`'s sentence about rewriting sentences you did not need to touch names the passage exception. The test set in `docs/prose-review/` runs against the agent.

**Checked 2026-11-04, while building `PL-JP8X`.** A passage from one heading to the next can be a whole long section. In `docs/MODEL.md` at `0c0caa4d3`, § "Displayed precision" runs 745 rows and 8,095 words with no subheading, and `PL-ZDZ0`'s change to it was 163 words. So `tools/new_prose.py --compare` reports each run of changed paragraphs beside the paragraphs it replaced, not the section. Decide what the copy editor reads in a section that long before building it.

**Generator check.** Not counted. The open `prose-quality` rewrite items (`PL-J37P`, `PL-BSYT`, `PL-PS5H`, `PL-XBJ3`, `PL-XT53`, `PL-YVL0`, `PL-9331`) are each a section that fix branches grew and could not shrink, which fits this mechanism, but nobody has checked each one's history.
