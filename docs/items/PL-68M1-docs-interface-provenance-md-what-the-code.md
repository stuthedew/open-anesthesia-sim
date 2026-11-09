---
id: PL-68M1
title: docs/interface-provenance.md § 'What the code cannot answer' draws four conclusions for this project (a named set of things that may float, the header staying visible, modes, no tablets) that the adopts-diverges-refuses list has no entry for: adopted, open, or only advice? (copy editor structure read, 2026-11-05)
priority: P2
effort: M
status: ready
classes: defect, docs
feature: interface-provenance-structure
touches: docs/interface-provenance.md
added: 2026-11-05
payoff: the thread that designs the layout finds every conclusion it must answer to in the one list it is told to read, including the two that bear on misreading a value's context
verify: grep -qF 'Conclusions from Blender' docs/interface-provenance.md
---

**Problem.** docs/interface-provenance.md § 'What the code cannot answer' draws four conclusions for this project (a named set of things that may float, the header staying visible, modes, no tablets) that the adopts-diverges-refuses list has no entry for: adopted, open, or only advice? (copy editor structure read, 2026-11-05)

**The structure read's query** (row numbers are docs/interface-provenance.md at cfb15a4a, before the line edit):

- **Query on conclusions missing from the decisions list:** § "What the code cannot answer: Blender's stated reasoning" states several things that carry over to this project or that it must design for itself:
  - a "small, named, enumerable set of things that may float, with a predicate" (rows 670-673);
  - "the header stays visible except in rare, well-reasoned cases" (rows 803-814);
  - this project's own handling of modes (rows 803-814);
  - the limit that the model does not apply to tablets (rows 826-838).

  § "What this project adopts, diverges from, and refuses" has no entry for any of them, though rows 156-158 call it the list that a design must answer to. Is each one adopted, still open, or only advice? Each one that is adopted belongs in that list.

**Checked 2026-11-09:** `grep -n 'enumerable\|rare, well-reasoned\|tablet' docs/interface-provenance.md` finds all four conclusions in § "What the code cannot answer: Blender's stated reasoning". They are a small, named set of things that may float, with a predicate (§ "\"Non-overlapping\" is narrower than it sounds"), the header that stays visible except in rare, well-reasoned cases, and this project's need to design its own handling of modes (§ "There is no mode-awareness doctrine to borrow"). The fourth is that the area model does not apply to a standalone tablet (§ "Where Blender says the model does not apply"). § "What this project adopts, diverges from, and refuses" still has no entry for any of them. The restructure (`PL-T8RL`) moved the text and left this question.

**Why it matters.** § "What a later design thread owes this study" makes the adopts, diverges and refuses list the one a design must answer to. A conclusion that sits only in the reasoning chapter can be missed by the thread that builds the layout. Two of the four, the floating set and the handling of modes, bear on whether a learner can misread which run or state a value belongs to.

**Done when.** § "What this project adopts, diverges from, and refuses" holds a short list, led "**Conclusions from Blender's stated reasoning, and where each stands.**", with one line for each of the four. Each line says whether the conclusion is adopted, diverged from, refused, or still open. It names the decision or the `ROADMAP.md` entry that settles it, or the item or milestone that will. A conclusion that no decision settles yet is recorded as open, which is an answer and does not need the owner now. This item records where each stands; it does not decide any of them.

**Generator check.** One-off: a finding from the `docs/interface-provenance.md` structure read (`PL-ZMBN`).

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** `git show 817a4d88:docs/interface-provenance.md` already states the floating set (row 660) and the tablet limit (rows 741-746) in the reasoning chapter, and the adopts, diverges and refuses list already had no entry for them. So the problem was present at the freeze, commit `817a4d88` (2026-10-24), and this finding belongs on v0.7.0's frozen list rather than deferred.
