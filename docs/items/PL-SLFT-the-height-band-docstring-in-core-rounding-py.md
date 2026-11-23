---
id: PL-SLFT
title: The HEIGHT_BAND docstring in core/rounding.py says a 0.01 percentage-point display step is 0.5% of 1 MAC of sevoflurane; at the stored 1.8% it is 0.56%, so the docstring still describes the 2.0% MAC sevoflurane had before MAC at age 40 (found by PL-JP7P's blind review)
priority: P3
effort: S
status: done
classes: defect, docs
feature: model-claims-held-by-tests
touches: src/anesthesia_sim/core/rounding.py
added: 2026-11-23
closed: 2026-11-23
pr: 2279
filed-pr: 2268
payoff: a developer reading why the MAC-target band is safe is given the stored MAC's figure, not the old 2.0% one
verify: ! grep -qF '0.5% of 1 MAC of sevoflurane' src/anesthesia_sim/core/rounding.py
---

**Problem.** The HEIGHT_BAND docstring in core/rounding.py says a 0.01 percentage-point display step is 0.5% of 1 MAC of sevoflurane; at the stored 1.8% it is 0.56%, so the docstring still describes the 2.0% MAC sevoflurane had before MAC at age 40 (found by PL-JP7P's blind review)

**Why it matters.** The docstring explains why the band that decides when a
run reaches a MAC target is far finer than anything displayed. It gives the
display step as a share of 1 MAC of sevoflurane at the MAC sevoflurane had
before the stored MAC became Mapleson 1996's value at age 40 (1.8%). The
conclusion still holds, but a developer checking it gets the wrong figure.

**Done when.** The docstring gives the share at the stored MAC, 0.56%, and the
ratio to the band that follows from it.

**Generator check.** One-off. The figure was derived from sevoflurane's MAC
before the stored MAC moved to Mapleson 1996's value at age 40, and a
docstring is not held to a test the way the four standing documents' figures
now are (`PL-JP7P`). No head's `misread:` line states the fact:
`bin/docket generators --misread` was searched on 2026-11-23 for "figure",
"copy", "docstring", "stored value" and "prose".

**Done 2026-11-23.** The docstring now says the display step is 0.56% of
sevoflurane's 1 MAC at age 40, about 560 times the band (0.01 / 1.8 is
0.00556, and 0.00556 / 1e-5 is 556). The conclusion that the band is far
finer than anything displayed is unchanged. Files checked for the same stale
figure: `src/anesthesia_sim/core/rounding.py`, `docs/MODEL.md`,
`docs/INTERFACE.md`, `docs/VERIFICATION.md` and `docs/PARAMETERS.md`
(`grep -n "0.5% of 1 MAC"` finds no other).
