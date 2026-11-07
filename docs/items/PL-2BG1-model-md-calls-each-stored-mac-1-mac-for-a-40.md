---
id: PL-2BG1
title: MODEL.md calls each stored MAC '1 MAC for a 40-year-old adult' (Delivery-limit and MAC parameters, and three provenance table rows), but its adopted source, De Wolf et al. 2012, gives a flat adult MAC with no age, and the same section's table shows the stored values 2.6% to 11.1% off Mapleson's age-40 figures
status: untriaged
touches: docs/MODEL.md
added: 2026-11-07
---

**Problem.** MODEL.md calls each stored MAC '1 MAC for a 40-year-old adult' (Delivery-limit and MAC parameters, and three provenance table rows), but its adopted source, De Wolf et al. 2012, gives a flat adult MAC with no age, and the same section's table shows the stored values 2.6% to 11.1% off Mapleson's age-40 figures

**Where it was found.** The copy editor queried it while `PL-F0Q2` tested the fixed copy editor on § "Delivery-limit and MAC parameters" as it stood before `#2049`, and `main` still has the sentence. The section says "`mac_percent` is 1 MAC for a 40-year-old adult". The same section says the stored values are "single adult MACs with no adjustment for age, which De Wolf et al. state they used in their Gas Man simulations", and that "the reference adult has no age to which an age-related MAC could be applied". The rows for the three MACs in § "Source hierarchy"'s provenance table also label them "1 MAC, 40-year-old adult". Each agent file's adopted source entry calls the value "the flat adult MAC De Wolf et al. state they used", with no age. Against Mapleson's age-40 values, the stored MAC is 11.1% high for sevoflurane, 2.6% high for isoflurane and 9.1% low for desflurane. So a clinician reading "1 MAC for a 40-year-old adult" beside that table cannot tell what the stored value claims to be.

**Two more queries from the same run, on the same section.**
- "The 22% is larger than either source's own confidence limits": the section gives confidence limits only for Mapleson's values (about ±7%, ±10% for desflurane), and none for the De Wolf MACs. Either give the stored values' limits or say the 22% is larger than Mapleson's.
- "None remain as of this revision" gives no date or version, though § "Status" says a statement that gives a version has been true since that version.

**Fix.** Call the stored value "a single adult MAC with no age stated by its source" in the section and in the three table rows, unless a source that places it at age 40 is found and recorded. The fix touches no stored value.
