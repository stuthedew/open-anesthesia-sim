---
id: PL-KFTM
title: Carry each compartment's modelled agent amount on SimulationSnapshot as one record per compartment, and derive stored_agent_l from those records
priority: P1
effort: M
status: ready
classes: safety, anticipated
feature: schematic
touches: src/anesthesia_sim/app/controller.py, tests/unit, tests/reference, docs/ARCHITECTURE.md
added: 2026-10-25
payoff: the snapshot carries each compartment's modelled agent amount, checked against an independent oracle, and the stored total is their sum
verify: grep -rq 'def test_each_compartment_s_amount_matches_an_independent_oracle' tests/reference
---

**Where this came from.** `PL-LF0P` scoped v0.7.0, the schematic, on 2026-10-25. The project owner chose containers that fill to tension, labelled with their amounts, plus a bar showing each compartment's share of the agent (project owner, 2026-10-25, ratified, over containers drawn to scale and over Gas Man's Picture as it is). `ROADMAP.md` § "v0.7.0 - the schematic" has the reasoning and the measurements behind it.

**Problem.** Each compartment in `core/` holds its own `agent_amount_l`, but
`SimulationSnapshot` in `src/anesthesia_sim/app/controller.py` passes on only
their total, `stored_agent_l`. `ROADMAP.md` § "Designed for forking" declined
per-compartment amounts until a consumer needed them, and the schematic is
that consumer.

**What to build.** The snapshot carries the six compartments' amounts beside
their tensions, read from `core/`. They travel as one record per compartment,
not as six more flat floats, so that v0.8.0 can key the same record by
substance instead of adding fields. `stored_agent_l` becomes the sum of those
records, so the total and its parts have one source. No equation changes.

**Tests.** A reference test compares each compartment's amount at stated
instants with an oracle independent of `core/`, as
`.claude/rules/test-oracles.md` requires. A unit test checks that the six
amounts add up to `stored_agent_l` exactly.

**Why it matters.** The schematic and the share bar cannot draw an amount the
snapshot does not carry, and a View that reads `core/` directly would bypass
the snapshot's stale-state guarantees.

**Done when.** The snapshot carries the per-compartment record, the oracle
test passes, and `docs/ARCHITECTURE.md` describes the record.
