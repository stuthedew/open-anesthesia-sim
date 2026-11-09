---
id: PL-KYGF
title: Answer the questions the structure read of ROADMAP.md's v0.6.0 section left for its author: what 'the gate decision' was, which entry decides an Area refused a size, and the definition of done's baseline
priority: P3
effort: M
status: untriaged
classes: docs
feature: roadmap-structure
touches: ROADMAP.md
added: 2026-11-08
payoff: The v0.6.0 record that a session reads to change the layout system answers its own open questions.
---

**Problem.** Answer the questions the structure read of ROADMAP.md's v0.6.0 section left for its author: what 'the gate decision' was, which entry decides an Area refused a size, and the definition of done's baseline

**Source.** The copy editor's structure read of `ROADMAP.md` (chapter reads 27 to 34, the v0.6.0 section), quoted whole in `PL-B6V1`. Slice 6 (`PL-B6V1`) applied the moves and answered from the tree each query the tree answers, and its record lists those answers. These need the author: the record does not hold the answer, so a session would be guessing. `PL-71H3` holds the same kind of question for the v0.7.0 section.

**The questions.**

1. The opening paragraph says "The placement, the split and the gate decision were all recommendations put to the owner and agreed." The placement is the early slot and the split is item 34's halving at break-out. What was "the gate decision"?
2. Required scope entry 5 gives the View contract a clause for "what the container does when an Area cannot honour a size", and entry 8 decides "what a split or a border drag does when the minimum cannot be met". Which entry decides that behaviour? The other should keep a pointer.
3. Entry 1 says the tree gives up some joins, which are refused. Entry 14 says the border-chain query recovers "the one behaviour that the tree gives up compared with Blender's graph". Is that one behaviour or two?
4. The definition of done checks "No learner-visible regression against v0.5.0" and then "Everything a learner could do with two runs on 2026-09-16". v0.5.0 shipped on 2026-09-21. Which baseline applies?
5. Does the definition of done's "A Workspace that names none of those Views still leaves them reachable" cover a Workspace the learner saved, as well as the shipped ones? Are the "two surfaces" of the View contract bullet the "two Views that already exist"?
6. Entry 5 cites "the four clauses that the 2026-09-16 audit added". Which item records that audit?
7. Entry 2 says the 2026-09-16 measurement "is stronger than the form that item recorded". Stronger in what way?
8. Entry 20's Area header paragraph says "Planned-milestone item 33's own argument for the move names the header, but no entry specifies it", while entry 20 specifies the header. What is "the move"? And what does entry 20 decide about the View chooser, the one surface whose paragraph lists no decisions?
9. Is remembering which screen a window was on planned for later, or ruled out? The out-of-scope list now puts it with the windows planned for later.
10. The floating-Areas entry said "So the exclusion is stated with its condition", a sentence about the text that slice 6 cut; planned-milestone item 34 keeps the history before it. Which condition did it mean, beyond "wanted later" and `docs/MODEL.md`'s occlusion rule?

**Why it matters.** v0.6.0's section is the record a session reads to change the layout system. A question it leaves open is answered again by guesswork in every session that needs it.

**Done when.** Each question is answered in this brief, and the answer that belongs in `ROADMAP.md` is written there by the line edit (`PL-YRY3`) or by its own commit.

**Sorted 2026-11-09: whose each question is.** Questions 1 to 8 and 10 are a session's, because a record or the tree answers them. Question 1 is in `PL-NMTF`'s record of the scoping round. Questions 2, 3 and 5 are answered by the code and `docs/interface-provenance.md`. Question 4 is answered by v0.6.0's cut item, `PL-9CS6`, which records what the release was checked against. Questions 6, 7 and 10 are answered by a search of the store and of `PL-B6V1`'s and planned item 34's history. Question 8 is answered by the section itself. Question 9 is the owner's, because it decides whether a feature stays on the roadmap.

**Decision needed.**

Question 9: when break-out into separate windows is built, should the simulator remember which screen each window was on, or is that ruled out? v0.6.0's out-of-scope list gives the danger: a position restored onto a changed set of monitors can put a window where the learner cannot see it. **Recommended:** planned for later with break-out, on one condition. A saved position is restored only onto a screen that is still connected; otherwise the window opens on the main screen. The danger is then a condition on the feature rather than a reason to rule it out, as with floating Areas. Nothing changes for a learner until break-out is scheduled.

**Generator check.** One-off: questions from the `ROADMAP.md` structure-read sweep, which a move-only slice left for the author. No mechanism keeps producing them.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** The passages these questions are about were present when Gate 3 froze at `817a4d88`: for example "the placement, the split and the gate decision were" all ratified, and "Remembering which screen" in the out-of-scope list. At `needs-decision` the item counts as debt, so it joins v0.7.0's frozen list.
