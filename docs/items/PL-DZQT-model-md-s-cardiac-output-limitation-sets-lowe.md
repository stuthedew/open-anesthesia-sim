---
id: PL-DZQT
title: MODEL.md's cardiac-output limitation sets Lowe's 4.84 L/min beside Cattermole's measured 5.51 L/min without saying that Lowe's is derived from an interspecies oxygen-consumption allometry and an assumed constant a-v difference
status: untriaged
added: 2026-09-10
---

**Problem.** MODEL.md's cardiac-output limitation sets Lowe's 4.84 L/min beside Cattermole's measured 5.51 L/min without saying that Lowe's is derived from an interspecies oxygen-consumption allometry and an assumed constant a-v difference

**Where.** `docs/MODEL.md`, "Known limitations", the paragraph beginning
"Cardiac output does not scale with the patient". It reads:

> Two published figures sit either side of the stored value: Lowe and Ernst's
> own cardiac-output relation - the upstream the Gas Man Workbook names, now
> read at the source - gives $`0.2M^{3/4}`$, which is 4.84 L/min at 70 kg, and
> Cattermole et al.'s 686 subjects in the 50-75 kg band give a measured median
> of 5.51 L/min.

**Nothing in it is false**, which is why this is an item rather than a
same-session fix: it says "measured" of Cattermole and does not say it of Lowe.
What it does is set the two side by side as "two published figures", in a
sentence whose only asymmetry is a word a reader has to notice.

**What pages 17-19 of the book now establish** (read 2026-09-10, `PL-8SDL`).
Lowe's relation is not a cardiac-output measurement and is not an independent
derivation either. It is arithmetic on two borrowed constants:

- Figure 2.2, page 17, plots oxygen consumption against body weight for
  mammals from 0.03 kg to 8,000 kg and gives the slope as "approximately 10
  kg^(3/4)", reproduced by permission from *Brody, S. Bioenergetics and Growth.
  Reinhold, New York, 1945.*
- Page 17 takes the arteriovenous oxygen content difference as "about 5 ml of
  O2/dl of blood", attributed to Guyton et al. (reference 13), whose full
  citation is in chapter 2's unread reference list. The same reference is
  credited with concluding that kg^(3/4) "is probably a better index of cardiac
  output than any other parameter, including surface area".
- Figure 2.4, page 19, is the arithmetic: kg^(3/4) x 10 gives O2 use in ml/min,
  and O2 use / 5 - the divisor annotated "(a-v)DO2 = 5 ml/dl" - gives cardiac
  output in dl/min. The figure also draws the composed edge directly, kg^(3/4)
  x 2 -> Q in dl/min, which is the 2 kg^(3/4) page 59 uses without citing.

So 4.84 L/min at 70 kg is an interspecies metabolic allometry fitted across
five orders of magnitude of body mass, divided by an arteriovenous difference
assumed constant across mammals. Cattermole et al. is 686 human subjects
measured in the weight band the stored value sits in. Presenting them as two
comparable published figures is the kind of false equivalence
`CLAUDE.md`'s safety-critical standard rules out for a displayed value, and
`docs/MODEL.md` is where a reader goes to decide how much to trust the number.

**Approach.** One clause, not a rewrite: say what Lowe's figure is before
giving it. The paragraph's conclusion does not change - `PL-YKSM` decided on
2026-09-08 to keep the fixed 5.0, and this makes that decision read better
rather than worse, because the weaker of the two competing figures is the one
being declined.

**Also check the provenance section**, which `PL-8SDL` updated with the same
derivation on 2026-09-10, so that the two statements agree in emphasis and one
does not read as a correction of the other.

**Done when.** A reader of "Known limitations" cannot come away thinking 4.84
L/min is a measured human cardiac output.
