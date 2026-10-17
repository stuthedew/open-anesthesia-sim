---
id: PL-SWY5
title: Esper et al. 2015 (Anesth Analg 120:45-50), the primary blood:gas measurement Meybohm et al. 2021's Table 1 footnote says Gas Man's coefficients differ from, is cited in none of the three agent files beside the adopted De Wolf blood:gas values (found closing PL-0SG0; read 2026-10-12 from PMC7943506's XML record, footnote and reference 54)
priority: P1
effort: S
status: ready
classes: science
feature: provenance
touches: src/anesthesia_sim/data/agents/sevoflurane.json, src/anesthesia_sim/data/agents/isoflurane.json, src/anesthesia_sim/data/agents/desflurane.json, docs/MODEL.md
added: 2026-10-12
payoff: a reader of each agent file can see the most recent primary blood:gas measurement and how far the stored Gas Man value sits from it, rather than an account that stops before it
verify: grep -q 'Esper' src/anesthesia_sim/data/agents/sevoflurane.json && grep -q 'Esper' src/anesthesia_sim/data/agents/isoflurane.json && grep -q 'Esper' src/anesthesia_sim/data/agents/desflurane.json
---

**Problem.** Esper et al. 2015 (Anesth Analg 120:45-50), the primary blood:gas measurement Meybohm et al. 2021's Table 1 footnote says Gas Man's coefficients differ from, is cited in none of the three agent files beside the adopted De Wolf blood:gas values (found closing PL-0SG0; read 2026-10-12 from PMC7943506's XML record, footnote and reference 54)

**Checked 2026-10-17** on this tree (`b9b3c812`): `grep -ril esper` over
`src/` and `docs/` outside `docs/items/` finds nothing, so no agent file, no
`docs/MODEL.md` section and no other document cites Esper et al. 2015. Each
file's `blood_gas_partition_coefficient` (0.65 sevoflurane, 1.3 isoflurane,
0.42 desflurane) is adopted on De Wolf et al. 2012, tier 3, and each already
cites older primary blood:gas measurements beside it, not adopted: Strum and
Eger for sevoflurane, Malviya and Lerman and Lerman et al. for isoflurane, Eger
for desflurane. `docs/MODEL.md` § "Source hierarchy: what may be cited as the
authority for a value" names "Eger, Strum and Eger, and Lerman et al." as the
primary measurements the second admissible reason sets aside. **Not re-read
here:** the claim that Meybohm et al. 2021's Table 1 footnote and its
reference 54 set Gas Man's blood:gas coefficients against Esper's rests on the
capture's 2026-10-12 read of PMC7943506. The sevoflurane file's own record of
that footnote (its De Wolf note, written under `PL-0SG0`) quotes only "based
on the work of Yasuda et al.", so the work reads the footnote and reference 54
first and quotes what they say.

**Why it matters.** The agent files' blood:gas provenance is meant to say
which primary measurements exist and how far the stored, adopted tier-3 figure
sits from each, so that a reader can judge the stored number. That account is
missing the newest of them, a measurement in a clinically relevant patient
population, and the one a published Gas Man study names as differing from
the program's set. Blood:gas solubility sets the speed of wash-in and
emergence on every curve a learner reads, so an incomplete record of what it
was measured to be is a `science` provenance gap even though no stored value
is wrong by the project's own adoption rule.

**Done when.** Each of `src/anesthesia_sim/data/agents/sevoflurane.json`,
`isoflurane.json` and `desflurane.json` carries an Esper et al. 2015 entry in
`sources`, tier `primary`, `adopted` false, `authority_for` empty. Its note
gives the measured blood:gas value, dispersion, reference conditions and
population for that agent, how far the stored figure sits from it in percent,
the date and route it was read (full text or abstract), and what Meybohm et
al.'s footnote says of it. Each file's `provenance_gap` counts it among the
primary blood:gas measurements cited and not adopted, and `docs/MODEL.md`
§ "Source hierarchy" names it beside Eger, Strum and Eger, and Lerman et al.
No stored value changes: keeping the Gas Man set is the project owner's
decision of 2026-09-03 (`PL-D6LX`), and `ROADMAP.md`'s planned-milestone item
31 is the route to a primary-literature set. `make check`'s provenance checks
pass with the new entries.
