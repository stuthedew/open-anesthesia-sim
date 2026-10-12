---
id: PL-HJ7L
title: BreathingCircuit.deliverable_fresh_gas_flow_range can be reassigned on a built circuit past both its guards: the overlap check and the held flow's check run only in __post_init__, so a reassigned range can invert accepted_fresh_gas_flow_range_l_min and leave the held flow outside it
status: dropped
added: 2026-10-12
closed: 2026-10-12
reason: folded into PL-19Y0 at the 2026-10-12 triage pass: the range is one of BreathingCircuit's checked fields that item already holds to its constructor's checks, and its brief now carries this reproduction
---

**Problem.** BreathingCircuit.deliverable_fresh_gas_flow_range can be reassigned on a built circuit past both its guards: the overlap check and the held flow's check run only in __post_init__, so a reassigned range can invert accepted_fresh_gas_flow_range_l_min and leave the held flow outside it

**Found 2026-10-12** by a review pass over `#1442` (PL-7CRY), whose new
`accepted_fresh_gas_flow_range_l_min` docstring said the first end is never
above the second on a built circuit. Reproduced:

```text
c = BreathingCircuit()
c.deliverable_fresh_gas_flow_range = DeliverableFreshGasFlowRange(20.0, 30.0)
c.accepted_fresh_gas_flow_range_l_min   -> (20.0, 10.0)
float(c.fresh_gas_flow_l_min)           -> 4.0, outside the machine's range
```

Built with that range, the same circuit is refused with
`SimulationConfigurationError`. `_require_the_two_flow_claims_overlap` and
`_require_deliverable_flow` run in `__post_init__` only, and `__setattr__`
guards the fresh gas flow's own field alone (`PL-LBQY`). Nothing under `src/`
reassigns the range today (`git grep -n "deliverable_fresh_gas_flow_range ="`),
so it is latent; in the interface it would surface as `setting_readouts`'
`ValueError` and a halt of every run, not as a refused setting offered.

`PL-LBQY` is the precedent and the likely shape: `__setattr__` re-checks a
write to `deliverable_fresh_gas_flow_range` made after construction - the
overlap, and the held flow against the new range - and restores the old value
on refusal, with a regression test per check. Making the field unwritable
after construction is the other route, if no machine switch is planned.
