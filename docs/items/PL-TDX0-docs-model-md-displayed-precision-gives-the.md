---
id: PL-TDX0
title: docs/MODEL.md § "Displayed precision" gives the partition coefficients' measured SDs as 3.9% to 6.4% of the mean, which are Yasuda, Targ and Eger's brain:blood SDs, while the fat tissue:gas SDs the agent files record are 17% to 19%, so the section understates the fat fraction's uncertainty about 3.5 times and its one-SD displacement table may rest on the wrong SDs
priority: P1
effort: M
status: ready
classes: docs, science
feature: model-claims-held-by-tests
touches: docs/MODEL.md, tests/reference, docs/items
added: 2026-11-02
payoff: the uncertainty Displayed precision states for each compartment's parameters is the uncertainty its own source measured, so the precision argument a learner reads rests on the right SD
verify: ! grep -q '3.9% of the mean for desflurane' docs/MODEL.md
recurrences: 2026-11-04 PL-KG6S, 2026-11-04 PL-7R8S
---

**Problem.** `docs/MODEL.md` § "Displayed precision" says the stored
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
