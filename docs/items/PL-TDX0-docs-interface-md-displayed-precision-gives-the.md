---
id: PL-TDX0
title: docs/INTERFACE.md § "Displayed precision" gives the partition coefficients' measured SDs as 3.9% to 6.4% of the mean, which are Yasuda, Targ and Eger's brain:blood SDs, while the fat tissue:gas SDs the agent files record are 17% to 19%, so the section understates the fat fraction's uncertainty about 3.5 times and its one-SD displacement table may rest on the wrong SDs
priority: P1
effort: M
status: done
classes: docs, science
feature: model-claims-held-by-tests
touches: docs/INTERFACE.md, docs/MODEL.md, tests/integration/test_parameter_uncertainty.py, tests/unit/test_formatting.py, src/anesthesia_sim/app/formatting.py, src/anesthesia_sim/core/simulation_step.py, docs/items
added: 2026-11-02
closed: 2026-11-14
pr: 2150
payoff: the uncertainty Displayed precision states for each compartment's parameters is the uncertainty its own source measured, so the precision argument a learner reads rests on the right SD
verify: ! grep -q '3.9% of the mean for desflurane' docs/INTERFACE.md
recurrences: 2026-11-04 PL-KG6S, 2026-11-04 PL-7R8S
---

**Problem.** `docs/INTERFACE.md` § "Displayed precision" says the stored
partition coefficients' measured SDs are 3.9% of the mean for desflurane, 5.3%
for sevoflurane and 6.4% for isoflurane. It says they are the SDs of Yasuda,
Targ and Eger's human tissue coefficients. "Why not a significant-figures
rule" then says the fat fraction's parameters "are known to about 5%". Those
three figures are the paper's brain:blood SDs. According to PubMed's record
of Yasuda, Targ and Eger (Anesth Analg 1989;69:370-373, PMID 2774233, abstract
read 2026-11-02), brain/blood is 1.29 ± 0.05 for I-653 (desflurane),
1.57 ± 0.10 for isoflurane and 1.70 ± 0.09 for sevoflurane. That is 3.9%,
6.4% and 5.3%. The fat tissue:gas values that the agent files' sources notes
quote from the same paper are 12.0 ± 2.0 (desflurane), 34.0 ± 6.0
(sevoflurane) and 64.2 ± 12.3 (isoflurane), which is 16.7% to 19.2%. Both
blind review passes on `#1934` found this on 2026-11-02, and the numbers above
were checked in this session.

**Why it matters.** The section justifies the precision at which a learner is
shown each compartment, and the uncertainty it states for fat is about 3.5
times too small. Its conclusion against a significant-figures rule gets
stronger, not weaker, with the larger SD. But the "factor of fifty" and the
one-SD displacement table under "The upper limit" may both rest on the wrong
SDs. If the table perturbed each coefficient by 3.9% to 6.4%, its fat and
muscle rows understate the displacement.

**Checked 2026-11-02: muscle's SDs are larger still.** The same sources
notes quote the paper's muscle tissue:gas values as 0.94 ± 0.35
(desflurane), 2.38 ± 1.03 (sevoflurane) and 4.40 ± 1.97 (isoflurane). That
is 37% to 45% of the mean, about twice fat's and about eight times the
figures the section gives. The brain tissue:gas SDs are 0.54 ± 0.02,
1.15 ± 0.07 and 2.09 ± 0.10, or 3.7% to 6.1%, close to the brain:blood ones.
So the vessel-rich row may be near right, while the muscle and fat rows are
the ones to re-measure. The values are in the note beside the Yasuda
citation (PMID 2774233) in each of
`src/anesthesia_sim/data/agents/desflurane.json`, `sevoflurane.json` and
`isoflurane.json`, the note that starts "ADOPTED 2026-09-13". Those notes say
the muscle and fat figures come from the paper's full text, which is not in
PubMed Central, so this item reads the table before citing it. The two
sentences that `PL-TCD3` added say only that fat's SDs are larger. This
item's rewrite says muscle's too.

**Done when.** Each SD the section states is the SD of the coefficient it
names, read from the source with its table cited. The displacement table says
which SD it perturbed each coefficient by, and is re-measured where that SD
was wrong. "Why not a significant-figures rule" states the fat fraction's
uncertainty from the fat SDs, and its factor is recomputed. The paragraphs
that declare ``no test yet (`PL-TDX0`)`` name the test that now holds them.
`PL-19W8`'s count of wrong claims includes this one.

**Generator check.** Not a generator on what is known. It is one misread of
which coefficient a published SD belongs to, found once.

**Checked 2026-11-07 against the tree at the freeze (`PL-GW0P`).** The problem was present when Gate 3 froze at `817a4d88`, so the item joins v0.7.0's frozen list. It is classed `science` and is not deferred: nobody has yet measured whether the muscle and fat SDs make a displayed second decimal finer than its uncertainty, so the check the deferral rule asks for cannot be recorded. The 3.9%, 5.3% and 6.4% SDs and "known to about 5%" have been in `docs/MODEL.md` since `7a60a2f5` (2026-09-06), and the agent files at `817a4d88` already held the fat and muscle SDs.

**Built 2026-11-14.** The SDs were read from Yasuda, Targ and Eger 1989 at
full text in the project owner's reference corpus: Table 1 (p. 371) gives the
human tissue:gas coefficients the model stores, and Table 2 gives tissue:blood
coefficients computed from them by dividing by age-adjusted published blood:gas
values (pp. 371-372, methods). The 3.9%, 5.3% and 6.4% the section gave are Table
2's brain row. The SDs used now are Table 1's: brain (for the stored
vessel-rich value, which is the brain value) 3.7%, 6.1% and 4.8%, muscle 37%,
43% and 45%, and fat 17%, 18% and 19%, for desflurane, sevoflurane and
isoflurane. The blood:gas SDs are Eger 1987 for desflurane (0.424 ± 0.024),
Strum and Eger 1987 for sevoflurane (0.686 ± 0.047), both read in their PubMed
abstracts on 2026-11-14, and Esper et al. 2015 for isoflurane (1.45 ± 0.12),
because Lerman et al. 1984's abstract gives the adult mean without an SD (read
2026-11-14). Esper's SDs for the other two agents are wider (7.0% and 8.1%);
the same laboratory's measurements were preferred where they exist, because
the stored tissue values are that laboratory's.

Which SDs the 2026-09-06 table was run with is not recorded anywhere (`PL-X9KD`
records only the result). Replaying the brain:blood SDs on today's model gives
desflurane rows within a factor of 1.6 of the old table, so the old runs most
likely used them, but the model has changed since and the replay cannot
settle it. Every row was therefore re-measured.

`tests/integration/test_parameter_uncertainty.py` is new. It runs each agent
from empty at 1 MAC with the reference adult's flows, changes one coefficient
by its SD (as a share of the mean, both directions, larger shift kept), and
propagates the model's own system matrix exactly, reading every second to
1 h and then every minute to 24 h. The schematic's figures use every second
for the first 20 minutes and every minute after. It holds the displacement table, the SDs, the
counts per SD, the accounting panel's exhausted-total shifts (`PL-0P3F`), and
the schematic's amount and share shifts. It lives in `tests/integration/`
because it pins documented figures to the model's own output, and
`docs/ARCHITECTURE.md` keeps `tests/reference/` for cases derived without a
solver in `core/`. One guard would have caught this item:
`test_each_tissue_coefficient_s_sd_is_the_sd_of_the_coefficient_the_model_stores`
requires each stored tissue coefficient to lie within one SD of the mean of the
row its SD comes from, and the brain:blood means lie many SDs away.

**What the correct SDs changed.** The muscle SD is about eight times the
figure the section gave. One SD of it moves a readout by up to 0.90
percentage points in the first hour (desflurane), 90 counts of the last digit,
and it dominates the exhausted total's shift and the schematic's muscle amount
and share. So the section's rule, that a digit far finer than one SD is false
precision, now refuses the readouts' two decimals, the schematic's two-figure
amounts and whole-percent shares, and the long-run 0.1 L totals, while the
section keeps them. That is a change to the argument for what is displayed,
so it is filed as `PL-W51N`, a decision for the owner, and the section says
plainly where each precision now falls against one SD. No displayed value
changed.

**Docs swept.** `docs/INTERFACE.md` § "Displayed precision", every subsection:
the table and the SD paragraph, the bound, "Why not significant figures" (fat
now known to 17% to 19%, so three figures over-claim by about 170 to 190
times), the uniform-resolution bullet, the accounting panel's shifts and its
note for developers, the exhausted total in millilitres of liquid (one SD is
now 3.2 to 3.3 mL at 24 h, so 1 mL is about a third of an SD), and the
schematic's amount, share and two-figure paragraphs, and a whole-run column
in the table: over 24 h the blood:gas and fat rows also give a last digit
finer than a seventh of an SD. `docs/MODEL.md` § "Supported simulation step"
compared the step's timing error with "one parameter SD" of 6.8e-2 pp; it now
compares the ventilator start's 0.14 pp with the blood:gas coefficient's
8.2e-2 pp and the muscle coefficient's 0.90 pp, and the same comparison in
`core/simulation_step.py`'s comment was restated. The conclusion, that the
step stays at 0.1 s, only gets stronger. Comments in `app/formatting.py`
(run totals, amount, share) and docstrings in `tests/unit/test_formatting.py`
that quoted the old shifts were restated. Checked and unchanged: the rest of
`docs/MODEL.md` (its parameter-provenance table already gives Table 1's means
and SDs), `README.md`, `docs/ARCHITECTURE.md`, and `docs/WORKING_NOTES.md`,
whose 2026-09-06 entry is a dated record. `PL-19W8`'s count of claims found wrong should include
this one, and its test of the displacement table is now written.
