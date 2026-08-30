---
id: PL-HZC2
title: The closing action block annotates order instead of carrying it, so a numbered list can disagree with itself
priority: P2
effort: S
status: done
classes: defect
feature: worker-instructions
milestone: v0.2.7
touches: CLAUDE.md
added: 2026-08-30
closed: 2026-08-30
commit: e1ccbd4
verify: python3 tools/doc_check.py check
not-delegable: the change rewrites a rule in CLAUDE.md that every session then follows, and whether an ordering reads correctly is a judgment about prose no check decides
---

**Problem.** `CLAUDE.md`'s closing-block rule said "Where several things are
suggested, say which comes first", which licensed *annotating* an order onto a
list that already states one. The project owner caught it on 2026-08-30: a
four-item block ran 1, 2, 3, 4 with "*Recommended first*" hung on item 1 in one
reply and on item 2 in another, so the numbering and the note disagreed.

**Why it matters.** A numbered list states an order whether or not one was
meant. When the note contradicts the numbering the reader has to stop and work
out which to believe — which is precisely the friction the block exists to
remove, arriving in the one place in the reply that was supposed to be
frictionless. The owner's words: "number 2 should never say, do this first."

**Where.** `CLAUDE.md`, the "End every reply with what the project owner has to
do" bullet list.

**Approach.** Order is structural, not annotated: the first line is the first
thing to do. Ordering notes on later lines are forbidden outright rather than
discouraged, because the failure is not that the note is unhelpful but that it
competes with the numbering. Where items are genuinely independent, order by
consequence and say so in one clause, so the absence of a sequence is stated
rather than left to be inferred from a list that looks sequential.

The "mark a recommendation as a recommendation" half is kept and separated:
which option is recommended and which comes first are different questions, and
fusing them is what produced the contradiction.

**Done when.** The rule says the block is ordered the way it will be done, and
forbids annotating a later line as the first thing to do.
