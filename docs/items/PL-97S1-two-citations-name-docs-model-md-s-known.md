---
id: PL-97S1
title: Two citations name docs/MODEL.md's Known-limitations note 'One reference condition, where the model physically has two' without the section mark (core/liquid_agent.py:41 and ROADMAP.md:2759), so the doc check cannot see them, and the MODEL.md copy edit, which rewords that bold lead, would leave both pointing at nothing
status: untriaged
feature: repo-copy-edit
added: 2026-11-09
---

**Problem.** Two citations name docs/MODEL.md's Known-limitations note 'One reference condition, where the model physically has two' without the section mark (core/liquid_agent.py:41 and ROADMAP.md:2759), so the doc check cannot see them, and the MODEL.md copy edit, which rewords that bold lead, would leave both pointing at nothing

**What happened.** `PL-F0Q2`'s end-pass run on part 118 of the frozen `docs/MODEL.md` (the second run of "Known limitations") rewrote the bold lead "One reference condition, where the model physically has two." as "Amounts of agent are all counted in litres at 20 °C, including those held at body temperature." A test copy of the tree with only that lead renamed showed what the doc check sees. It reports one error, `docs/MODEL.md:905`, because that citation writes § before the name. It reports nothing for the docstring in `src/anesthesia_sim/core/liquid_agent.py`, which writes `§ "Known limitations", "One reference condition, ..."` with the mark on the first name only, or for `ROADMAP.md`, which quotes the note by name with no mark. Section 6's edit renamed "What this requires of a branch", but every citation of that lead carries the mark, so the doc check would refuse the edit until they were fixed.

**Why it matters.** The liquid-agent docstring is where a developer learns that a stored amount converts 5.8 % high. A pointer to a note that no longer exists sends that reader nowhere. The file is under `core/`, so it is filed here rather than fixed in place.

**Done when.** Both citations write the section mark before the note's name, so the doc check refuses a rename that leaves them behind. Either the copy edit of `docs/MODEL.md` keeps the lead's wording, or it updates all three citations in the same change.
