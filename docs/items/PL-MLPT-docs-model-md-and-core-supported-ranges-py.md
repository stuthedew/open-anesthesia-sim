---
id: PL-MLPT
title: docs/MODEL.md and core/supported_ranges.py argue the 24-hour supported run length with two claims that do not hold: that it sits near the outer edge of the measured 0.35-to-9.5 MAC-hour range, when a run at 1 MAC reaches about 24 MAC-hours at the cap, and that the fat time constant bounds it from below, when 24 hours is about 0.6 of that time constant
priority: P1
effort: M
status: done
classes: science, docs
feature: supported-run-length-text
milestone: v0.6.9
touches: docs/MODEL.md, src/anesthesia_sim/core/supported_ranges.py
added: 2026-10-25
closed: 2026-10-26
pr: 1860
payoff: the authoritative specification no longer certifies a 24-hour span as inside the evidence it cites, and its argument for the limit no longer contradicts itself
verify: ! grep -qF 'near the outer edge of the exposure range' docs/MODEL.md && ! grep -qF 'It is near the outer edge of the' src/anesthesia_sim/core/supported_ranges.py && ! grep -qF 'With a span shorter than about one' docs/MODEL.md && ! grep -qF 'with a cap shorter than about one' src/anesthesia_sim/core/supported_ranges.py
recurrences: 2026-10-25 PL-KHXB withdrawn 2026-10-27 PL-8MRM
---

**Problem.** The comment above `MAXIMUM_ELAPSED_SIMULATION_TIME_S`
(`core/supported_ranges.py`) and `docs/MODEL.md` § "Supported run
length" say 24 h sits inside the regime the source
calls clinically negligible, "near the outer edge" of the measured exposure
range. The same section gives that range as 0.35 to 9.5 MAC-hours, and says
that past about ten MAC-hours "even the size of the omission is unmeasured".
The cap bounds elapsed time, not exposure. A run
opens at the agent's 1 MAC (sevoflurane at 2.0%). It therefore reaches about
24 MAC-hours at the cap, and about 96 at the 8% dial maximum.

The same argument also contradicts itself. `docs/MODEL.md` § "Why 24
hours, and not a multiple of the slowest time constant" says the fat time
constant "bounds this number from below". With "a span shorter than about
one time constant, the fat trace stops showing what it exists to show". It
then says "24 hours is about 0.6 of it". The comment in
`core/supported_ranges.py` makes the same two statements.

**Why it matters.** The authoritative specification certifies as supported a
span 2.5 to 10 times past the evidence it cites. The interface then calls
every value up to hour 24 "inside the supported span". Either the cap is
argued and enforced in exposure terms, or the text says plainly that a long
run at or above 1 MAC leaves the measured range well before 24 hours. The self-contradiction
matters for the same reason: a later reader who argues for moving the limit
cannot tell which statement governs. The floor needs restating as what it
really is, for example a fraction of the time constant at which fat is
still visibly loading.

**Done when.** `docs/MODEL.md` § "Supported run length" and the comment above `MAXIMUM_ELAPSED_SIMULATION_TIME_S` no longer call 24 hours "near the outer edge" of the measured exposure range. Both state the MAC-hours a run at 1 MAC reaches at the cap, and say plainly that such a run leaves the measured range well before 24 hours, unless the cap is argued and enforced in exposure terms instead. Both also state the fat time-constant floor in a form 24 hours satisfies, and no longer say that a span shorter than about one time constant stops the fat trace teaching.

**Found by.** `PL-TBQS` reviewer replay on #421, findings r01 F1, r03 F1,
r05 F1 and r06 F1. Checked against main on 2026-10-25. The defaults were
read from a fresh controller: sevoflurane opens at 2.0% with an 8.0% dial
maximum, isoflurane at 1.2% of 5.0%, desflurane at 6.0% of 18.0%
(scripts/b1_mac_hours.py). Finding r06 F3 on #421, the time-constant
floor, was checked against main on 2026-10-25 by reading both places.

**Closed on #1860, counting MAC-hours end-tidal** (2026-10-26). A blind
review pass on #1860 found that the first rewrite counted MAC-hours at the
dial. A MAC-hour is conventionally counted at the end-tidal concentration,
which in this model is the alveolar fraction, and that fraction stays below
the dial during uptake. So `docs/MODEL.md` and the comment count about 24
MAC-hours for a run whose alveolar fraction is held near 1 MAC, say a run
left at its opening dial accumulates somewhat less, and give the 96 at
sevoflurane's 8% dial maximum as an upper bound counted at the dial. The cap
is still argued in elapsed time. Enforcing it in exposure terms would be a
model change, not a text change, and nothing here asked for one.
