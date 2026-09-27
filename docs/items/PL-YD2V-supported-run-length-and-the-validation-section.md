---
id: PL-YD2V
title: Supported run length and the validation section's caveat 4 bound the slow tail on metabolism and fat flow alone, but the fourth compartment this model lacks is the largest term in Yasuda 1991's measured washouts from about hour 2-3 to hour 21-29, inside the 24 h envelope, and neither passage says so
priority: P1
effort: S
status: ready
classes: science, docs
feature: late-washout-evidence
touches: docs/MODEL.md
added: 2026-09-26
payoff: a reader of Supported run length learns that the washout tail lacks its largest measured term from about the third hour, not only past the 24-hour boundary
verify: grep -qF 'PL-YD2V' docs/MODEL.md
---

**Problem.** Supported run length and the validation section's caveat 4 bound the slow tail on metabolism and fat flow alone, but the fourth compartment this model lacks is the largest term in Yasuda 1991's measured washouts from about hour 2-3 to hour 21-29, inside the 24 h envelope, and neither passage says so

**Found 2026-09-26 while working `PL-WMCJ`.** The figures are in `docs/MODEL.md` § "Known limitations", the intertissue-diffusion note that item added, which carries the table, the pages of both Yasuda 1991 papers read from the private reference corpus, and how each ratio and crossing time was computed.

**Premise checked 2026-09-27.** § "Supported run length" ("What bounds it is
what this model omits. Metabolism, first of all...") and caveat 4 under §
"Published wash-in and elimination validation test" name metabolism and the fat
group's flow as what the slow tail lacks, and neither names the fourth
compartment. "Known limitations" says "The two omissions above are what bound
the supported run length" in the paragraph before the intertissue-diffusion
note `PL-WMCJ` added.

**Why it matters.** § "Supported run length" is where a reader learns how long
a run can be trusted, and it frames the omissions as mattering over days, past
the boundary. On the published mean coefficients the term this model lacks is
the largest in the measured washout from 1.8-3.1 hours after a 30-minute
administration until 20.7-29.4 hours, so inside the envelope the tail already
misses its largest measured component, and a reader trusting the section trusts
that stretch of the trace further than the evidence goes.

**Done when.** § "Supported run length" and caveat 4 each say that inside the
supported 24 hours the tail lacks the fourth compartment's term, the largest in
the measured washout over the hours "Known limitations" gives, pointing at that
note; the "two omissions" paragraph in "Known limitations" says which omissions
bound the run length and which the tail inside it; and `docs/MODEL.md` cites
`PL-YD2V` where it changes. Whether the 24 hours should move is `PL-KK1Q`'s to
raise, once its measurement gives the size.

**Note from `PL-HBH2`, 2026-09-27.** The two passages this item rewrites still
restate the fat flow as "about twice the reachable resting measurement", the
PET reading alone; `PL-HBH2` made the fat-perfusion paragraph two-sided (the
Yasuda washout fits put the flow at or a little above the stored figure), so
carry that reading into both restatements as well.
