---
id: PL-WF25
title: MODEL.md's Known limitations says the stored sevoflurane MAC is 10% low and the stored desflurane MAC 10% high against Mapleson's age-40 values, which reverses both directions: stored sevoflurane 2.0% is 11.1% above Mapleson's 1.80%, and it is the displayed MAC multiple that reads 10% low (the Delivery-limit table and the MAC-awake section say it correctly)
status: dropped
touches: docs/MODEL.md
added: 2026-11-07
closed: 2026-11-09
reason: Fixed by the MODEL.md restructure (PL-BSMF, #2054): Known limitations now points at the Delivery-limit table, which gives the displayed MAC multiple's 10% low and 10% high correctly, and the stored-MAC gaps (11.1% high, 9.1% low) agree with the data files
---

**Problem.** MODEL.md's Known limitations says the stored sevoflurane MAC is 10% low and the stored desflurane MAC 10% high against Mapleson's age-40 values, which reverses both directions: stored sevoflurane 2.0% is 11.1% above Mapleson's 1.80%, and it is the displayed MAC multiple that reads 10% low (the Delivery-limit table and the MAC-awake section say it correctly)

**Where it was found.** A session found it while answering the project owner's question on 2026-11-07 about MODEL.md's layout, from `PL-BSMF`'s finding that the stored-MAC gap is given in three framings. § "Known limitations" says "Against Mapleson's age-40 meta-analytic values, the stored sevoflurane MAC is 10% low and the stored desflurane MAC is 10% high." The data files store 2.0% for sevoflurane and 6.0% for desflurane, and Mapleson's age-40 values are 1.80% and 6.6%. So the stored sevoflurane MAC is 11.1% high and the stored desflurane MAC is 9.1% low, as § "MAC-awake as a chart reference" says. The 10% figures belong to the displayed MAC multiple, as the table in § "Delivery-limit and MAC parameters" heads its column "Displayed MAC reads". A clinician who believes the sentence would expect the simulator's sevoflurane MAC multiples to read high against the literature, when they read low.

**History.** Before `#1808` (`PL-BZR4`) the sentence said the stored MAC "reads 10% low", which already blurred the stored value with the displayed multiple. `#1808` changed "reads" to "is", which made it wrong.

**Fix.** Say "the displayed sevoflurane MAC multiple reads 10% low and the desflurane one 10% high", or give the stored values' own gaps, 11.1% high and 9.1% low. `PL-BSMF` would also leave this gap stated once, in § "Delivery-limit and MAC parameters", with a pointer here.

**Fixed by the restructure.** The MODEL.md restructure (`#2054`, `PL-BSMF`) cuts this § "Known limitations" paragraph to a pointer at the table in § "Delivery-limit and MAC parameters", which states the gap correctly. Close this item as fixed by `#2054` once that pull request and the branch carrying this item have both merged.

**Checked 2026-11-09:** `grep -n '10% low\|10% high\|11.1%\|9.1%' docs/MODEL.md` on cfd4a4b6 no longer finds the wrong sentence. § "Known limitations" now points at § "Delivery-limit and MAC parameters", whose table says the displayed MAC multiple reads 10% low for sevoflurane, 2.5% low for isoflurane and 10% high for desflurane. § "MAC-awake as a chart reference" says the stored MAC is 11.1% high for sevoflurane, 2.6% high for isoflurane and 9.1% low for desflurane. Both agree with the data files (`mac_percent` 2.0, 1.2 and 6.0) and Mapleson's age-40 values (1.80%, 1.17% and 6.6%): 1.80/2.0 = 0.90, 1.17/1.2 = 0.975, 6.6/6.0 = 1.10. The restructure (`PL-BSMF`, #2054) fixed it, as the brief expected.

**Generator check.** One-off: a sentence that blurred the stored MAC with the displayed MAC multiple, introduced by one reword (`#1808`). No head's `misread:` states that fact, and the restructure left the gap stated once, in § "Delivery-limit and MAC parameters".
