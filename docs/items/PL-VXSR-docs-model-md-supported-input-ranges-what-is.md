---
id: PL-VXSR
title: docs/MODEL.md § Supported input ranges, 'What is left open, stated plainly', says AlveolarCompartment(gas_volume_l=1e-6) can still be built; since #1833 CompartmentVolume refuses any volume outside 0.01 to 10 000 L, so only a 10 000 L circuit at the envelope's edge is still accepted
priority: P2
effort: S
status: done
touches: docs/MODEL.md
added: 2026-11-03
closed: 2026-11-03
pr: 1964
payoff: docs/MODEL.md says correctly which gas volumes a caller writing Python can still build
verify: ! grep -q 'gas_volume_l=1e-6' docs/MODEL.md && grep -q 'either volume anywhere in the numerical envelope, 0.01 to 10 000 L' docs/MODEL.md
---

**Problem.** docs/MODEL.md § Supported input ranges, 'What is left open, stated plainly', says AlveolarCompartment(gas_volume_l=1e-6) can still be built; since #1833 CompartmentVolume refuses any volume outside 0.01 to 10 000 L, so only a 10 000 L circuit at the envelope's edge is still accepted

**Generator check.** Not a generator. The sentence went stale when the
numerical envelope typed every compartment volume on #1833, and the plain
rewrite of this section (`PL-QHR2`) is what read it again. One stale sentence
is one instance, not three items from one mechanism.

**Fixed.** The paragraph now says that a caller can build either gas volume
anywhere from 0.01 to 10 000 L by passing a `CompartmentVolume`, and that only
the numerical envelope bounds it. Checked by building `CompartmentVolume` at
1e-6, 0.01, 10 000 and 10 000.1 L: the two inside values are accepted and the
two outside are refused.
