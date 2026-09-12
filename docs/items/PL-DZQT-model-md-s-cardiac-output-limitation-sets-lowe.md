---
id: PL-DZQT
title: MODEL.md's cardiac-output limitation sets Lowe's 4.84 L/min beside Cattermole's measured 5.51 L/min without saying that Lowe's is derived from an interspecies oxygen-consumption allometry and an assumed constant a-v difference
priority: P1
effort: S
status: done
classes: science, docs
feature: model-spec-accuracy
milestone: v0.4.13
touches: docs/MODEL.md, src/anesthesia_sim/data/patients/reference_adult.json
added: 2026-09-10
closed: 2026-09-10
pr: 494
verify: python3 tools/doc_check.py check && grep -qF 'they are not evidence of the same kind' docs/MODEL.md
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

## Outcome, 2026-09-10: the asymmetry is stated in all three places

**The project owner agreed with the recommendation.** One clause, no rewrite,
and the paragraph's conclusion is unchanged: `PL-YKSM`'s decision of 2026-09-08
to keep the fixed 5.0 L/min stands, for the structural reason it gave.

**`docs/MODEL.md`, "Known limitations".** "Two published figures sit either side
of the stored value" now continues "**and they are not evidence of the same
kind**", and the sentence that follows says what each is: Lowe's 4.84 L/min is
derived rather than measured — Brody's 1945 interspecies oxygen-consumption
allometry divided by an arteriovenous difference assumed constant across
mammals — against Cattermole et al.'s measured median in 686 human subjects in
this file's weight band. It closes on the thing a reader could otherwise get
wrong: the stored 5.0 is not bracketed by two comparable observations, and the
number being declined is the weaker of the two.

**Two cross-references followed, which is the half the brief asked for.**

- `docs/MODEL.md`'s "Parameter provenance" ended its derivation paragraph by
  pointing at this item as carrying the fix. It now points at "Known
  limitations" as the place that states it, so the two sections agree in
  emphasis and neither reads as a correction of the other.
- `reference_adult.json`'s Lowe and Ernst entry said "`PL-DZQT` carries the one
  place it currently does". It now names both places that say so.

**And the Cattermole entry, which the brief did not name and should have.**
That entry is where `PL-YKSM` recorded the decision, and it is the entry a
reader of `default_cardiac_output_l_min` meets first — so it is the third place
the two figures stand side by side. It said the reason was "structural rather
than a choice between 4.84 and this entry's measured 5.51", which is true and
still invites the comparison. It now says the two are not evidence of the same
kind, and why "a choice between them" was the wrong frame to begin with.

**One unrelated repair rode along**, in the same `note` field and visible only
in the diff: restoring the withdrawn ICRP entry (`PL-TKRT`) left the phrase
"which is where this chain actually stops" duplicated in the Lowe and Ernst
note. Deduplicated.

**The `verify:` command was run both ways** before being recorded: the grep
string is absent from `docs/MODEL.md` on `origin/main`, and the paired command
exits 0 here.
