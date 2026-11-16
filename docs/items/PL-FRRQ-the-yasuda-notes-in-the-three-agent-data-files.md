---
id: PL-FRRQ
title: The Yasuda notes in the three agent data files judge the stored tissue:gas coefficients by whether a measured value rounds to them ("rounding to the stored precision explains only two", "2.04 does not round to"); the project owner said on 2026-11-09 'I wouldn't round coefficients', and MODEL.md now gives each difference as a percentage, so the notes should say the same
priority: P2
effort: S
status: ready
classes: defect, docs
feature: model-md-structure
touches: src/anesthesia_sim/data/agents
added: 2026-11-09
payoff: the provenance notes and MODEL.md give each stored coefficient's distance from its measurement in the same terms, as a percentage
verify: ! grep -rqF 'does not round to' src/anesthesia_sim/data/agents && ! grep -rqF 'rounding to the stored precision explains only two' src/anesthesia_sim/data/agents
---

**Problem.** The Yasuda notes in the three agent data files judge the stored tissue:gas coefficients by whether a measured value rounds to them ("rounding to the stored precision explains only two", "2.04 does not round to"). The project owner said on 2026-11-09 'I wouldn't round coefficients', and `docs/MODEL.md` now gives each difference as a percentage, so the notes should say the same.

**Generator check.** The rounding comparison is a one-off, written on 2026-09-13 when the Yasuda notes were added to the three agent data files. `docs/MODEL.md` was corrected on 2026-11-09 in pull request 2054.

**Checked 2026-11-09:** `grep -o` on the three agent files finds the rounding
framing in each Yasuda note: "rounding to the stored precision explains only
two of those (isoflurane vessel_rich 2.09 to 2.1, sevoflurane muscle 2.38 to
2.4)", "FOUR OF THE NINE REPRODUCE THEM TO THE STORED PRECISION, TWO EXACTLY AND
TWO AS ROUNDINGS", and "2.04 does not round to". `docs/MODEL.md` § "Parameter
provenance" now gives the same comparison as percentages: two stored values
within 1% of Yasuda's mean (+0.5% and +0.8%), and five that differ by 2.3% to
9.0% (lines 3615 to 3616).

**Why it matters.** A reviewer checks the provenance note to see how far each
stored coefficient is from its measurement. Judging by rounding treats a 0.5%
difference as a match and a 2.9% one as a miss, which says more about the
stored decimals than about the size of the difference. The notes and
`docs/MODEL.md` also describe one comparison in two ways.

**Done when.** Each agent file's Yasuda note gives each stored coefficient's
difference from the measured mean as a percentage, as § "Parameter provenance"
does, and no longer judges a value by whether it rounds to the stored figure.
No stored value changes, and each note keeps its route and depth of reading.

**Present at the Gate 3 freeze (checked 2026-11-09).** The passage this item
fixes was already in its file at `817a4d88`, the commit that froze Gate 3, so
under ROADMAP.md § "The gate is a snapshot, not a moving target" the item
joins v0.7.0's frozen list rather than being deferred by its capture date.

**Done 2026-11-16.** The Yasuda note in each of the three agent files now
gives each stored tissue:gas coefficient's difference from Yasuda's measured
mean as a percentage, to one decimal place as `docs/MODEL.md` § "Parameter
provenance" does: sevoflurane vessel_rich -4.3%, muscle +0.8%, fat 0%;
isoflurane vessel_rich +0.5%, muscle +2.3%, fat +9.0%; desflurane
vessel_rich 0%, muscle +3.2%, fat +8.3%. The cross-agent sentence that said
"FOUR OF THE NINE REPRODUCE THEM TO THE STORED PRECISION" now says two equal
the mean and lists the other seven by percentage. The older comparison
through Yasuda's brain:blood (brain:blood times the stored blood:gas) now
gives sevoflurane -0.5%, desflurane -0.3% and isoflurane +2.9% instead of
"at the precision the file keeps" and "2.04 does not round to". The same
rounding sentence was also in each file's `provenance_gap`, so it was changed
there too, because the two fields would otherwise describe one comparison in
two ways. A script computed every percentage from the stored value and the
mean the note quotes; all agree with `docs/MODEL.md`'s +0.5%, +0.8% and
2.3% to 9.0%. No stored value changed, which the script checked by comparing
each file with its notes removed. The figures that the notes gave to two
decimals, such as 4.35% and 9.03%, are now given to one, matching
`docs/MODEL.md`. The
sentence "whatever it took from Yasuda it took at an unstated rounding" was
kept: it records why the tier was not raised before the paper was read, and
judges no value by rounding. Docs sweep: `docs/MODEL.md` § "Parameter
provenance" (already in percentages, unchanged), `ROADMAP.md` (the item's own
line only), `tests/` (no test quotes the changed text).

Blind review, 2026-11-16. The second pass found that the new list gives desflurane fat as +8.3 percent while the older sentence in the same note gives isoflurane fat as -8.3 percent, on a different basis. Each sentence now names its basis: the list is stored against measured, as a percentage of the measured mean, and the older sentence gives each change as a percentage of the stored value.
