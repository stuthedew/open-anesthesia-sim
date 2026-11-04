---
id: PL-43GT
title: The plain-writing rule governs only how sentences are worded: nothing sets the order a clinician reader needs (what the readout shows, what it means, then why) or stops one line of reasoning being split into a chain of short sentences, and the blind prose measure scores awkwardness rather than length, so it passed at 21.7% while the owner judges the output too long
priority: P1
effort: S
status: done
classes: defect
feature: reader-first-prose
touches: .claude/rules/plain-writing.md, docs/prose-review/prompt.md, .claude/skills/docket/modes/close-out.md
deferred-from: v0.7.0 - captured after the freeze; it changes how sessions write prose, not a displayed value
added: 2026-11-03
closed: 2026-11-04
pr: 2008
payoff: a session writing for a clinician or the owner leaves out what that reader does not act on, so a passage says what a readout means in a few sentences
verify: grep -q 'needs to act on, and stop' .claude/rules/plain-writing.md
---

**Problem.** `.claude/rules/plain-writing.md` has eight rules about sentences and five patterns of padding. What a paragraph includes, and in what order, gets one paragraph ("Before you write a paragraph, decide what its reader needs"), and nothing checks it. Three of the sentence rules push toward more words: keep the small words, one point per sentence, and most sentences under 25 words. A session following them splits one line of reasoning into a chain of short sentences joined by "So" and "That". The reader then has to rebuild the links.

**Example, from `PL-ZDZ0`'s branch at `e4ae4220a`.** "Converting the percent readout's step into MAC would give each agent a different step. The last digit of the MAC readout would then stand for a different amount for each agent. So the MAC readout uses the same step, measured in MAC, for every agent." That is 45 words for one idea: "One step for all agents keeps the last MAC digit worth the same amount whatever the agent" (17 words). The same passage opened with how the MAC step is derived, before saying what step the clinician sees.

**The measure misses it.** `PL-Y55Q` and `PL-J6CK` rate each unit plain or awkward, and the close-out review was kept on 21.7% awkward (`PL-J6CK`, 2026-10-19). The rubric file, `/mnt/project-files/v0.6.0/plain-writing/measure/results.md`, was not in the container on 2026-11-03, so whether it scores length is unconfirmed. The owner judged the reviewed `PL-ZDZ0` text too long and unclear on 2026-11-03.

**Why it matters.** Every session writes to this rule, so a rule that only adds words grows every text it touches, and each grown passage then needs a rewrite item of its own. Seven `docs/MODEL.md` rewrite items (`PL-BSYT`, `PL-J37P`, `PL-9331`, `PL-PS5H`, `PL-XBJ3`, `PL-XT53`, `PL-YVL0`) wait on this rule and on the copy editor, so they are not rewritten to the old one.

**Recommended (first draft, 2026-11-03).** Add two rules: order for the first reader, and keep one line of reasoning in one sentence. Replace "Most sentences should be under 25 words" with "Cut a sentence that a reader would not miss". Add "Which sentences could go, and how short could this passage be with every fact kept?" to the review prompt. Federal plain-language guidance puts organising for the reader before word choice (digital.gov, Plain Language Guide, "Organize"). Gopen and Swan (American Scientist 1990;78:550-558) place readability in where old and new information sit in a sentence and how sentences link, more than in sentence length.

**Ratified design, 2026-11-04.** `PL-J1ZM`'s design round made this item part 1 of its fix (project owner, 2026-11-04, ratified, over keeping the close-out prose review advisory and adding rules to it). It changes the draft above in three places:

1. One lead paragraph, "**Write what the reader needs to act on, and stop.**", carries the order and the cut. It replaces "Before you write a paragraph, decide what its reader needs".
2. "Give a chosen value its reason from a record" applies to docstrings, comments and the `docs/MODEL.md` note for developers, and no longer to every paragraph.
3. "Cut a sentence that a reader would not miss" is dropped, because rule 7 and the lead paragraph already say it. The review prompt asks for each sentence that could go with every fact kept, with one of three reasons, and no length. The owner refused a word target (`PL-J1ZM` part 4, and `docs/dead-ends.md`).

Rule 4 keeps a cause and its consequence in one sentence where they fit, with the MAC example above, in place of the 25-word sentence.

**Done when.** `.claude/rules/plain-writing.md` leads with the paragraph in point 1, narrows the paragraph in point 2, and carries rule 4's new sentence in place of the 25-word one. `docs/prose-review/prompt.md` asks for each sentence that could go, with its reason, and the prose-review test set passes on it.

**Generator check.** Part of the fix for `PL-J1ZM`, the live generator of over-explaining prose. Its fact is that head's: the writing rule told sessions how to word a sentence and nothing about what to leave out.
