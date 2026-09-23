---
id: PL-H5DV
title: ROADMAP planned item 27 says fat holds more agent than every other compartment combined for hours, but in this model fat overtakes muscle only at 4.7-7.5 h and everything else at 7.0-9.5 h
status: done
feature: compartment-trace-legibility
touches: ROADMAP.md
added: 2026-09-23
closed: 2026-09-23
verify: grep -qF 'overtakes muscle only after about five to seven and a' ROADMAP.md && ! grep -qF 'holding more agent than every other compartment combined' ROADMAP.md
---

**Problem.** ROADMAP planned item 27 says fat holds more agent than every other compartment combined for hours, but in this model fat overtakes muscle only at 4.7-7.5 h and everything else at 7.0-9.5 h

**Found 2026-09-23 in `PL-QYBW`'s design round** (the chart's percent axis
compressing fat), which routes fat's missing lesson to item 27 and so needs
item 27's rationale to be true.

`ROADMAP.md` § "Planned milestones" item 27 (the schematic compartment view,
Gas Man's "Picture") justifies itself with: "the graph plots partial pressure,
so fat reads near zero for hours while holding more agent than every other
compartment combined." The first half holds. The second does not, for any case
a learner runs.

**Measured** on the current tree: reference adult, vaporizer dial held at
1 MAC, 0.1 s steps, `AgentUptakeSystem.for_agent`, amounts from each
compartment's `agent_amount_l`:

| Agent | Fat's share of stored agent at 30 / 60 / 180 min | Fat overtakes muscle | Fat overtakes all other patient compartments | ... and the circuit too |
| --- | --- | ---: | ---: | ---: |
| Sevoflurane | 14% / 20% / 30% | 7.5 h | 8.7 h | 9.5 h |
| Isoflurane | 16% / 21% / 32% | 7.2 h | 8.3 h | 8.7 h |
| Desflurane | 13% / 20% / 33% | 4.7 h | 5.8 h | 7.0 h |

Muscle is the largest store throughout the first hours (34-56% of the stored
agent from 30 min to 3 h on every agent). Whether that is also the classical
account needs a primary source before item 27 says so. The nearest
confirmation found is Gas Man's own, a simulation rather than a measurement:
"Fat levels of anesthetic remained less than 0.15 MAC for all drugs up to the
6 hours tested" (Leeson S, Roberson RS, Philip JH. *Anesth Analg*
2014;119(4):829-835, https://doi.org/10.1213/ANE.0000000000000384, retrieved
from PubMed, PMID 25099926, and verified against the abstract 2026-09-23).
Fat's lesson is still real: it holds a large and steadily growing share at a
partial pressure the chart draws within a few pixels of zero, and it is the
largest store at equilibrium (capacity 493 L gas-equivalent against muscle's
79 L for sevoflurane). What is wrong is the tense and the comparison.

**Fix.** Rewrite item 27's sentence to what is measured, for example: "fat
reads near zero for hours while holding a fifth of the stored agent at one
hour and a third at three, and more than every other compartment combined
only after seven to ten hours." A tier-1 or tier-2 source for the classical muscle-first
ordering should be cited beside it rather than this model alone
(`docs/MODEL.md` § "Source hierarchy: what may be cited as the authority for a
value").

**Done when.** Item 27's rationale states fat's share and the crossover as
measured, with its source.
