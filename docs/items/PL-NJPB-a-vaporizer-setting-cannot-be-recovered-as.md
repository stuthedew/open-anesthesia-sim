---
id: PL-NJPB
title: A vaporizer setting cannot be recovered as dialled from RunSegment.settings: fraction times 100 misses the percent for 13 of 81 settings
status: untriaged
added: 2026-09-27
---

**Problem.** A vaporizer setting cannot be recovered as dialled from RunSegment.settings: fraction times 100 misses the percent for 13 of 81 settings

**Found by `PL-SM5V`, 2026-09-27, and not worked there.** That item made a
recorded segment hold each flow in the litres per minute that was set, because
dividing by sixty does not run backwards. The vaporizer has the same shape one
layer up: the dial is set in percent and the settings hold
`delivered_partial_pressure_fraction`. Measured in the container's Python:
`p / 100 * 100 != p` for 13 of the 81 settings from 0.0 to 8.0 % at 0.1 %
(0.9, 1.7, 1.8, 3.3 to 3.7, 6.6, 6.8, 7.0, 7.2 and 7.4); 0.9 reads back as
0.9000000000000001. Rebuilding settings from the fraction is exact, since the
compartment holds the fraction too, so nothing inside `core/` is affected.
What is not recoverable is the percent the learner dialled, which a save and
load format (planned item 9) or anything else recovering the dial from a
segment would need. Where the percent becomes a fraction was not located;
start by finding that conversion and whether the control timeline records the
percent as dialled.
