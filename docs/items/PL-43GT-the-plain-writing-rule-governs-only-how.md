---
id: PL-43GT
title: The plain-writing rule governs only how sentences are worded: nothing sets the order a clinician reader needs (what the readout shows, what it means, then why) or stops one line of reasoning being split into a chain of short sentences, and the blind prose measure scores awkwardness rather than length, so it passed at 21.7% while the owner judges the output too long
status: untriaged
feature: reader-first-prose
touches: .claude/rules/plain-writing.md, docs/prose-review/prompt.md
added: 2026-11-03
---

**Problem.** `.claude/rules/plain-writing.md` has eight rules about sentences and five patterns of padding. What a paragraph includes, and in what order, gets one paragraph ("Before you write a paragraph, decide what its reader needs"), and nothing checks it. Three of the sentence rules push toward more words: keep the small words, one point per sentence, and most sentences under 25 words. A session following them splits one line of reasoning into a chain of short sentences joined by "So" and "That". The reader then has to rebuild the links.

**Example, from `PL-ZDZ0`'s branch at `e4ae4220a`.** "Converting the percent readout's step into MAC would give each agent a different step. The last digit of the MAC readout would then stand for a different amount for each agent. So the MAC readout uses the same step, measured in MAC, for every agent." That is 45 words for one idea: "One step for all agents keeps the last MAC digit worth the same amount whatever the agent" (17 words). The same passage opened with how the MAC step is derived, before saying what step the clinician sees.

**The measure misses it.** `PL-Y55Q` and `PL-J6CK` rate each unit plain or awkward, and the close-out review was kept on 21.7% awkward (`PL-J6CK`, 2026-10-19). The rubric file, `/mnt/project-files/v0.6.0/plain-writing/measure/results.md`, was not in the container on 2026-11-03, so whether it scores length is unconfirmed. The owner judged the reviewed `PL-ZDZ0` text too long and unclear on 2026-11-03.

**Recommended.** Add two rules to `.claude/rules/plain-writing.md`, and say what they replace:

1. **Order for the first reader.** Say what the reader sees, then what it means for them, then why. Derivations, test names and history go to the developer note or the item.
2. **Keep one line of reasoning in one sentence where it fits.** Do not split a cause and its consequence into separate sentences joined by "So" or "That".

Replace "Most sentences should be under 25 words" with "Cut a sentence that a reader would not miss". Add a question to the review prompt: "Which sentences could go, and how short could this passage be with every fact kept?" Federal plain-language guidance puts organising for the reader before word choice (digital.gov, Plain Language Guide, "Organize"). Gopen and Swan (American Scientist 1990;78:550-558) put readability in where old and new information sit in a sentence and how sentences link, more than in sentence length.

**Done when.** The rule carries both additions and the replacement, and the review prompt asks the length question.
