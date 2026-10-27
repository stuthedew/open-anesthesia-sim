---
id: PL-02CD
title: The MAC-awake band's docstring in app/formatting.py and the Chortkoff 1995 source note in desflurane.json both say that importing Chortkoff's absolute 2.60% would teach a later wake-up, but a band drawn too high is crossed sooner during washout and teaches an earlier one, as docs/MODEL.md says
priority: P1
effort: S
status: done
classes: docs, science
feature: mac-awake-reference-text
touches: src/anesthesia_sim/app/formatting.py, src/anesthesia_sim/data/agents/desflurane.json
added: 2026-10-25
closed: 2026-10-26
pr: 1863
payoff: the provenance record of the MAC-awake band names the unsafe direction correctly, so a later change that teaches a faster emergence is not judged safe
verify: ! grep -qF 'later wake-up' src/anesthesia_sim/app/formatting.py && ! grep -qF 'later wake-up' src/anesthesia_sim/data/agents/desflurane.json && grep -qF 'earlier wake-up' src/anesthesia_sim/data/agents/desflurane.json
---

**Problem.** The docstring of `mac_awake_band_percent` in `src/anesthesia_sim/app/formatting.py` says the 20% denominator mistake "would teach a later wake-up than the source supports". The Chortkoff 1995 note in `src/anesthesia_sim/data/agents/desflurane.json` says the band would be "too high and teaches a later wake-up". Concentration falls during emergence, so a trace crosses a higher band sooner. `docs/MODEL.md` § "MAC-awake as a chart reference" gets this right: the band is "crossed too soon".

**Why it matters.** The source note is the provenance record of a stored clinical value. A maintainer reads it to learn which way an error in the fraction or the divisor is unsafe. Both texts give the direction backwards, so a later change could be judged safe when it teaches a faster emergence.

**Done when.** The docstring of `mac_awake_band_percent` and the Chortkoff 1995 note in `desflurane.json` say that a band drawn too high is crossed sooner during washout and teaches an earlier wake-up, as `docs/MODEL.md` does. Neither says "later wake-up".

**Found by.** `PL-TBQS` reviewer replay on #288, findings r01 F2, r02 F2, r05 F1 and r06 F3. Checked against main on 2026-10-25: both sentences are unchanged.
