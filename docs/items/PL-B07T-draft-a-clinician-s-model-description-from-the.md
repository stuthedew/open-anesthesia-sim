---
id: PL-B07T
title: Draft a clinician's model description from the paragraphs the reverse outline labels Model description, as a separate file for the owner to read before docs/MODEL.md changes
priority: P2
effort: M
status: ready
classes: docs
feature: model-md-structure
touches: docs/prose-review/model-description-draft.md
added: 2026-11-10
payoff: the owner can judge a clinician's model description of about an eighth of today's length before anything in docs/MODEL.md moves
verify: grep -qE '^[*][*]The owner read the draft' docs/items/PL-B07T-*.md
---

**Problem.** Draft a clinician's model description from the paragraphs the reverse outline labels Model description, as a separate file for the owner to read before docs/MODEL.md changes

**Why it matters.** `docs/MODEL.md` has two readers, a clinician and a
developer, and the reverse outline of 2026-11-10 found that 23% of its words
serve the clinician and 13% belong in a description of the model. A clinician
who wants to know whether to trust a displayed value has to read past test
descriptions, interface requirements and decision history to find it. The
owner agreed on 2026-11-10 to see a clinician's model description as a
separate draft before anything in `docs/MODEL.md` moves (project owner,
2026-11-10, ratified, over deciding the split from the outline's totals
alone). A draft changes nothing that the code's citations of `docs/MODEL.md`
sections depend on.

**How to do it.** Do not edit `docs/MODEL.md`.

1. Read `docs/prose-review/model-reverse-outline.tsv`, which `PL-9RLM`'s
   brief describes. Take the units whose `best_home` is "model description"
   (16,792 words). Take each unit's text by its line range from
   `git show 50af1a2e:docs/MODEL.md`, the commit the outline describes.
2. Check the units whose `reader` is "clinician" and whose `best_home` is
   something else, because a label is one model's judgement. Take any that a
   clinician needs in order to trust or interpret a displayed value.
3. Order the draft for the clinician: what the model represents, its
   compartments and equations, each parameter with its value and source, the
   assumptions, and each limitation that could change what a clinician
   concludes from a displayed value.
4. State each fact once. Where two units give one fact, keep the clearer
   statement. Keep every unit, value, equation, condition, exception and
   citation. Set no word target, which the owner refused on 2026-11-04
   (`PL-J1ZM`).
5. List in this item each fact that the draft leaves out and the home it
   would go to, so that the owner can see what the draft costs.
6. Commit the draft as `docs/prose-review/model-description-draft.md` and
   send the file to the owner to read.

The copy editor does not run on the draft. The owner asked the Projects
trial's coordinator on 2026-11-10 to hold copy editor runs and within-section
restructuring of `docs/MODEL.md` until the split is decided.

**Done when.** The owner has read the draft, and this item records in a
paragraph that opens "**The owner read the draft**" whether it is the
document a clinician should get. `PL-P3GZ` (decide whether to split
`docs/MODEL.md` by reader) then takes that answer.

**Generator check.** Work the owner asked for.
