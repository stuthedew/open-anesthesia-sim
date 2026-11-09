---
id: PL-97S1
title: Two citations name docs/MODEL.md's Known-limitations note 'One reference condition, where the model physically has two' without the section mark (core/liquid_agent.py:41 and ROADMAP.md:2759), so the doc check cannot see them, and the MODEL.md copy edit, which rewords that bold lead, would leave both pointing at nothing
priority: P3
effort: S
status: ready
classes: defect, docs
feature: repo-copy-edit
touches: src/anesthesia_sim/core/liquid_agent.py, ROADMAP.md
added: 2026-11-09
payoff: a rename of the Known-limitations note on the reference condition is caught by the doc check, so the liquid-agent docstring never points a developer at a note that no longer exists
verify: ! grep -qF '"Known limitations", "One reference' src/anesthesia_sim/core/liquid_agent.py && ! grep -qF 'The note "One reference condition' ROADMAP.md
reenters: PL-93LV
---

**Problem.** Two citations name docs/MODEL.md's Known-limitations note 'One reference condition, where the model physically has two' without the section mark (core/liquid_agent.py:41 and ROADMAP.md:2759), so the doc check cannot see them, and the MODEL.md copy edit, which rewords that bold lead, would leave both pointing at nothing

**What happened.** `PL-F0Q2`'s end-pass run on part 118 of `docs/MODEL.md` as it stood before `#2049` (the second run of "Known limitations") rewrote the bold lead "One reference condition, where the model physically has two." as "Amounts of agent are all counted in litres at 20 °C, including those held at body temperature." A test copy of the tree with only that lead renamed showed what the doc check sees. It reports one error, `docs/MODEL.md:905`, because that citation writes § before the name. It reports nothing for the other two citations. The docstring in `src/anesthesia_sim/core/liquid_agent.py` writes `§ "Known limitations", "One reference condition, ..."`, with the mark on the first name only, and `ROADMAP.md` quotes the note by name with no mark. The same end pass's edit of part 71 ("The canonical evaluation rule") renamed "What this requires of a branch", but every citation of that lead carries the mark, so the doc check would refuse the edit until they were fixed.

**Why it matters.** The liquid-agent docstring is where a developer learns that a stored amount converts 5.8 % high. A pointer to a note that no longer exists sends that reader nowhere. The file is under `core/`, so the fix is filed as this item rather than made in place.

**Done when.** Both citations write the section mark before the note's name, so the doc check refuses a rename that leaves them behind. Either the copy edit of `docs/MODEL.md` keeps the lead's wording, or it updates all three citations in the same change.

**Checked 2026-11-09:** On cfd4a4b6, `grep -rn 'One reference condition' --include=*.md --include=*.py .` finds the lead in `docs/MODEL.md`'s § "Known limitations", one citation in `docs/MODEL.md` § "Agent amount" with the section mark, and the two unmarked citations this item names. They are the module docstring of `src/anesthesia_sim/core/liquid_agent.py` and `ROADMAP.md`'s item that sizes the temperature half of the reference-condition change. The lead still reads as before, so both pointers resolve today. `PL-1VXY`, which applies the chapter reads, and the later line edit can both reword it.

**Generator check.** `PL-4FBP`'s fact: the link between a document sentence and the tree fact it restates, here a pointer the doc check cannot read because it lacks the section mark. `PL-93LV` fixed the same shape for the third citation of this lead and closed on 2026-11-02, within 30 days, and its fix did not reach these two. Recorded as `reenters: PL-93LV`.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** Present in part. At 817a4d88, `ROADMAP.md` already named the note "One reference condition, where the model physically has two" without the section mark. The docstring of `src/anesthesia_sim/core/liquid_agent.py` came later, with `c95177a6` (#1866, `PL-KZ99`). The problem belongs on v0.7.0's frozen list, and the deferral is removed.
