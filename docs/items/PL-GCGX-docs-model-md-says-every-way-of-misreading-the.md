---
id: PL-GCGX
title: docs/MODEL.md says every way of misreading the MAC-awake band runs toward an earlier wake-up, but the band also inherits the Gas Man MAC divisor, which puts sevoflurane's band 11% above the primary literature and desflurane's 9% below it, and the sevoflurane and isoflurane mac_reference_basis record no base MAC
priority: P1
effort: S
status: done
classes: docs, science
feature: mac-awake-reference-text
touches: docs/MODEL.md, src/anesthesia_sim/data/agents/sevoflurane.json, src/anesthesia_sim/data/agents/isoflurane.json
added: 2026-10-25
closed: 2026-10-26
pr: 1863
payoff: the safety argument for the MAC-awake band is true for every agent, and anyone can check how far each band sits from the primary literature
verify: ! grep -qF 'Every way of getting this wrong runs in the same direction' docs/MODEL.md && grep -qF 'fourth source of error' docs/MODEL.md
---

**Problem.** The band is the stored fraction times the Gas Man `mac_percent`. The traces are absolute partial pressures and do not depend on that divisor. The Mapleson 1996 notes in the data files record sevoflurane's 2.0% as 11.1% above the age-40 literature MAC, and desflurane's 6.0% as 9.1% below it. So sevoflurane's band centre sits at 0.68% where the literature supports about 0.61%. `docs/MODEL.md` § "MAC-awake as a chart reference" says that "every way of getting this wrong runs in the same direction" and list three errors without this one. For desflurane the divisor runs the other way. Its paragraph "What the references inherit, and one methodological limitation" says the references inherit the divisor's limits, but it does not give the direction or size. `mac_reference_basis` for sevoflurane and isoflurane names no base MAC value, so nobody can check the mismatch.

**Why it matters.** The direction claim is a safety argument in the authoritative specification. It is false for one agent and incomplete for the others. On the reviewer's 3-hour washout at 10 L/min, the vessel-rich trace crosses 0.68% at 6.51 min and 0.612% at 7.26 min. That is the same "band too high, wake-up too early" error that the fraction storage was chosen to avoid.

**Done when.** `docs/MODEL.md` § "MAC-awake as a chart reference" no longer says that every way of getting the band wrong runs in the same direction. It names the Gas Man MAC divisor as a source of error, with its direction and size for each agent. The `mac_reference_basis` of sevoflurane and isoflurane names the base MAC in percent, as desflurane's does.

**Found by.** `PL-TBQS` reviewer replay on #288, finding r04 F1. Checked against main on 2026-10-25: the section text and both `mac_reference_basis` strings are unchanged.

**Done on #1863, with the last part moved to `PL-P319`** (2026-10-26).
`docs/MODEL.md` § "MAC-awake as a chart reference" no longer says every way
of getting the band wrong runs in the same direction. It names the Gas Man
divisor as a fourth source of error, with its direction and size for each
agent. The last part of the Done-when line cannot be done from what the
project holds. The PubMed abstract of Katoh 1993 (PMID 8214700) says only "a
ratio to age-adjusted MAC", the companion paper on age (PMID 8424514) gives no
base MAC either, the paper has no PubMed Central copy, and the full text is
not in the reference corpus. So the sevoflurane and isoflurane
`mac_reference_basis` now say that the base MAC and the age correction are not
recorded, and why. Naming the base MAC in percent is `PL-P319`'s work, which
waits on the full paper and is on v0.7.0's frozen list beside this entry. The
`verify:` clause that tested for it moved to `PL-P319` with the work.
