---
id: PL-WF25
title: MODEL.md's Known limitations says the stored sevoflurane MAC is 10% low and the stored desflurane MAC 10% high against Mapleson's age-40 values, which reverses both directions: stored sevoflurane 2.0% is 11.1% above Mapleson's 1.80%, and it is the displayed MAC multiple that reads 10% low (the Delivery-limit table and the MAC-awake section say it correctly)
status: untriaged
touches: docs/MODEL.md
added: 2026-11-07
---

**Problem.** MODEL.md's Known limitations says the stored sevoflurane MAC is 10% low and the stored desflurane MAC 10% high against Mapleson's age-40 values, which reverses both directions: stored sevoflurane 2.0% is 11.1% above Mapleson's 1.80%, and it is the displayed MAC multiple that reads 10% low (the Delivery-limit table and the MAC-awake section say it correctly)

**Where it was found.** While answering the project owner's question on 2026-11-07 about MODEL.md's layout, from `PL-BSMF`'s finding that the stored-MAC gap is given in three framings. § "Known limitations" says "Against Mapleson's age-40 meta-analytic values, the stored sevoflurane MAC is 10% low and the stored desflurane MAC is 10% high." The data files store 2.0% for sevoflurane and 6.0% for desflurane, and Mapleson's age-40 values are 1.80% and 6.6%. So the stored sevoflurane MAC is 11.1% high and the stored desflurane MAC is 9.1% low, as § "MAC-awake as a chart reference" says. The 10% figures belong to the displayed MAC multiple, as the table in § "Delivery-limit and MAC parameters" heads its column "Displayed MAC reads". A clinician who believes the sentence would expect the simulator's sevoflurane MAC multiples to read high against the literature, when they read low.

**History.** Before `#1808` (`PL-BZR4`) the sentence said the stored MAC "reads 10% low", which already blurred the stored value with the displayed multiple. `#1808` changed "reads" to "is", which made it wrong.

**Fix.** Say "the displayed sevoflurane MAC multiple reads 10% low and the desflurane one 10% high", or give the stored values' own gaps, 11.1% high and 9.1% low. `PL-BSMF` would also leave this gap stated once, in § "Delivery-limit and MAC parameters", with a pointer here.
