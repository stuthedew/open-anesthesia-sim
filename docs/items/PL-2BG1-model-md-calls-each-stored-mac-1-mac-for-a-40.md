---
id: PL-2BG1
title: MODEL.md calls each stored MAC '1 MAC for a 40-year-old adult' (Delivery-limit and MAC parameters, and three provenance table rows), but its adopted source, De Wolf et al. 2012, gives a flat adult MAC with no age, and the same section's table shows the stored values 2.6% to 11.1% off Mapleson's age-40 figures
priority: P1
effort: S
status: done
classes: safety, defect, docs
feature: model-md-structure
touches: docs/MODEL.md, docs/INTERFACE.md, docs/items/PL-48MX-replace-what-is-left-of-docs-model-md-with-the.md, docs/items/PL-LBVN-gas-man-s-released-settings-file-holds-mac-2-1.md
added: 2026-11-07
closed: 2026-11-14
pr: 2155
payoff: a clinician reading what the MAC divisor is learns it is a flat adult value, so each displayed MAC multiple is not taken as relative to an age-40 MAC it differs from by up to 10%
verify: ! grep -qF '40-year-old adult' docs/MODEL.md
---

**Problem.** MODEL.md calls each stored MAC '1 MAC for a 40-year-old adult' (Delivery-limit and MAC parameters, and three provenance table rows), but its adopted source, De Wolf et al. 2012, gives a flat adult MAC with no age, and the same section's table shows the stored values 2.6% to 11.1% off Mapleson's age-40 figures

**Where it was found.** The copy editor queried it while `PL-F0Q2` tested the fixed copy editor on § "Delivery-limit and MAC parameters" as it stood before `#2049`, and `main` still has the sentence. The section says "`mac_percent` is 1 MAC for a 40-year-old adult". The same section says the stored values are "single adult MACs with no adjustment for age, which De Wolf et al. state they used in their Gas Man simulations", and that "the reference adult has no age to which an age-related MAC could be applied". The rows for the three MACs in § "Source hierarchy"'s provenance table also label them "1 MAC, 40-year-old adult". Each agent file's adopted source entry calls the value "the flat adult MAC De Wolf et al. state they used", with no age. Against Mapleson's age-40 values, the stored MAC is 11.1% high for sevoflurane, 2.6% high for isoflurane and 9.1% low for desflurane, as the section's table shows. So a clinician reading "1 MAC for a 40-year-old adult" beside that table cannot tell what the stored value claims to be.

**Two more queries from the same run, on the same section.**
- "The 22% is larger than either source's own confidence limits": the section gives confidence limits only for Mapleson's values (about ±7%, ±10% for desflurane), and none for the De Wolf MACs. Either give the stored values' limits or say the 22% is larger than Mapleson's.
- "None remain as of this revision" gives no date or version, though § "Status" says a statement that gives a version has been true since that version.

**Fix.** Call the stored value "a single adult MAC with no age stated by its source" in the section and in the three table rows, unless a source that places it at age 40 is found and recorded. The fix touches no stored value.

**Checked 2026-11-09:** `grep -n '40-year-old adult' docs/MODEL.md` finds the
label in the three rows of the provenance table ("1 MAC, 40-year-old adult",
lines 3250 to 3252) and in § "Delivery-limit and MAC parameters" ("The stored
MAC (`mac_percent`) is 1 MAC for a 40-year-old adult", line 3712). Forty lines
further on, the same section says the stored MACs are "single adult values
with no adjustment for age". Each agent file's adopted De Wolf entry calls the
value "the flat adult MAC it states it used", with no age. The two other
queries are still there too: "The 22% is larger than either source's own
confidence limits" (line 3756), and "none remain as of this revision" in
§ "Release gate" (line 12469). The section's table now gives the error as the
displayed reading (sevoflurane 10% low, isoflurane 2.5% low, desflurane 10%
high) rather than as the stored value's offset.

**Why it matters.** Every displayed MAC multiple is divided by this value. A
clinician who reads "1 MAC for a 40-year-old adult" will take each multiple as
relative to an age-40 MAC. Against Mapleson's age-40 values, the displayed
multiples read 10% low for sevoflurane and 10% high for desflurane, so that
reader misjudges what a displayed multiple means by the amount the section
itself reports.

**Done when.** The section and the three table rows call the stored value a
single adult MAC with no age stated by its source, unless a source that places
it at age 40 is found and recorded in the agent files. No stored value
changes. The 22% sentence compares only with the confidence limits the section
gives, which are Mapleson's. The `TBD` bullet in § "Release gate" carries a
date or a version, or drops its parenthesis. The sentence in § "MAC multiples
as a display unit" that defines MAC "in a nominal 40-year-old" describes MAC in
general, not the stored value, and may stay.

**Generator check.** One-off: a label that never matched its adopted source,
found when the copy editor was tested on this section (`PL-F0Q2`). The fact
misread is what the stored MAC's source says it is. The agent files hold it,
and no head states it.

**Present at the Gate 3 freeze (checked 2026-11-09).** The passage this item
fixes was already in its file at `817a4d88`, the commit that froze Gate 3, so
under ROADMAP.md § "The gate is a snapshot, not a moving target" the item
joins v0.7.0's frozen list rather than being deferred by its capture date.

**Done 2026-11-14.** The agent files were read again first: each adopted De
Wolf entry quotes the paper, "MAC values that we used in our Gas Man
simulations are: desflurane 6%, sevoflurane 2%, isoflurane 1.2%", with no age,
and no recorded source places the stored values at age 40. So `docs/MODEL.md`
now says the stored MAC is a single adult value whose source states no age, in
§ "Delivery-limit and MAC parameters", in the three provenance table rows, and
in the $`\mathrm{MAC}_\%`$ row of § "Symbols", which the brief did not list
and had the same "at age 40". The 22% sentence now compares with "the
confidence limits of Mapleson's values", and so does the matching sentence in
the MAC-divisor limitation under § "Known limitations", which also said
"either source's own confidence limits"; that limitation's "measures its gap"
became "gives its gap". The release-gate bullet drops "(none remain as of this
revision)": the condition stays, and `grep -n TBD docs/MODEL.md` finds no
marker. `docs/INTERFACE.md`'s sentence defining MAC "in a nominal 40-year-old"
describes MAC in general and stays, as does `app/formatting.py`'s matching
docstring. No stored value changed. The draft that `PL-48MX` will make
`docs/MODEL.md` still has the old label in four places; `PL-48MX` now lists
them.

Files checked in the docs sweep: `docs/MODEL.md`, `docs/INTERFACE.md`,
`README.md`, `src/anesthesia_sim/app/formatting.py`,
`src/anesthesia_sim/data/agents/sevoflurane.json`, `isoflurane.json`,
`desflurane.json`, `docs/prose-review/model-description-draft.md`.

**Blind review, 2026-11-14.** Both passes found that `docs/INTERFACE.md`'s
MAC-awake band paragraph still called the band "a band drawn for age 40". The
band is the MAC-awake fraction times the stored MAC, so it now says the band is
drawn on a single adult MAC whose source states no age and which lies close
to Katoh's age-40 MAC. Pass 2 also found that the MAC-divisor limitation's
"The gap is larger than the confidence limits of Mapleson's values" holds only
for sevoflurane, against `docs/INTERFACE.md`'s "Only sevoflurane's gap is
larger than its limits". It now names the sevoflurane-versus-desflurane shift,
and says "by Mapleson's meta-analysis" where it said "by the primary
literature", since that meta-analysis is tier 2.
