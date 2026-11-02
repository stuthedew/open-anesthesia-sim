---
id: PL-1XC7
title: The close-out prose review asks a model to read as a newcomer, which a model cannot do: replace it with a takeaway test against the named reader
priority: P1
owner-priority: P1, 2026-11-02
effort: S
status: blocked
feature: reader-tested-prose
touches: .claude/skills/docket/modes/close-out.md
blocked-by: PL-R7Q6
added: 2026-11-02
payoff: the prose review tests what the named reader would take from a paragraph and whether they could act on it
verify: grep -q 'would not know' .claude/skills/docket/modes/close-out.md
---

**Problem.** Close-out step 8 asks a model to review prose "for a careful
newcomer". The model knows the vocabulary, so "operator split" and "4e-4" read
clearly to it. Telling an expert to imagine a novice does not work for people
(Hinds 1999, J Exp Psychol Appl 5(2):205-221) or for models (Balog and Bakken,
arXiv:2608.30033, 2026). The prompt also forbids restating a number, so 4e-4
cannot become 0.04% (`PL-H76S`, faults 1 and 2).

**Why it matters.** The review is the last step before prose merges. While it
checks wording for an imagined newcomer, it passes text the real reader cannot
follow.

**What to build.** Decided in `PL-H76S`'s design round (project owner,
2026-11-02, 23:41Z, ratified, over a sixth plain-writing pattern). Rewrite
step 8's prompt as a takeaway test against the named reader. The reviewer gets
each unit with its reader line from `PL-R7Q6`, and returns four things for
each unit:

1. each word or number that the reader would not know, judged against the
   table's "does not know" list;
2. what this reader would take from the unit, in at most two sentences;
3. whether the unit lets this reader do what the table says they will do,
   such as change a value for a goal of their own;
4. each sentence that the takeaway does not need.

The reviewer may propose a rewrite, a move of a fact to a named place, and a
number restated in the reader's form with the same value. The writer compares
the takeaway with the point stated under `PL-TZ7R`. A listed term, a takeaway
that misses the point, or a reader who cannot act means a rewrite, and each
unneeded sentence moves or goes. The writer still rejects any change to a
value, unit, condition, identifier or citation. The `Prose-review:` trailer
keeps its three counts. The blind review brief stays as it is, so readability
has one reviewer.

**Done when.** Step 8's prompt asks for the four results above against the
printed reader, and its instructions to the writer say how to use them.

**Generator check.** Part of the fix for `PL-H76S`, the live generator for
prose that passes every check and fails its reader.
