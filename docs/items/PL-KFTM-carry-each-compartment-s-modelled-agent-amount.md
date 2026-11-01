---
id: PL-KFTM
title: Carry each compartment's modelled agent amount on SimulationSnapshot as one record per compartment, and derive stored_agent_l from those records
priority: P1
effort: M
status: done
classes: safety, anticipated
feature: schematic
touches: src/anesthesia_sim/app/controller.py, tests/unit, tests/reference, docs/ARCHITECTURE.md, ROADMAP.md
added: 2026-10-25
closed: 2026-11-01
pr: 1919
payoff: the snapshot carries each compartment's modelled agent amount, checked against an independent oracle, and the stored total is their sum
verify: uv run pytest tests/reference/test_compartment_amounts_against_oracles.py tests/unit/test_compartment_agent_amounts.py && grep -q 'def test_each_amount_matches_the_coupled_oracle' tests/reference/test_compartment_amounts_against_oracles.py && grep -q 'def test_the_six_amounts_add_up_to_the_stored_total_exactly' tests/unit/test_compartment_agent_amounts.py
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

**Checked 2026-10-25 (`PL-F2NX`, Gate 3's staleness sweep): still true.** `SimulationSnapshot` carries the six tensions and `stored_agent_l`, and no single compartment's amount. One thing to weigh before building: `core/` already sums the same six amounts in `AgentUptakeSystem.total_stored_agent_l`, which the accounting check reads. Summing the records again in `app/`, as Required scope entry 2 asks, writes a second sum of one fact, so the test should at least hold the two equal.

**Built 2026-11-01: `stored_agent_l` was kept as `core/`'s sum, not re-derived from the record.** The brief asked for `stored_agent_l` to become the sum of the new records. `core/` already sums the same six amounts once, in `AgentUptakeSystem.total_stored_agent_l`, and the accounting check reads that sum. Summing the records again in `app/` would have made a second sum of one fact, which `CLAUDE.md`'s one-source-of-truth principle refuses. So the snapshot keeps `core/`'s sum, and `tests/unit/test_compartment_agent_amounts.py` holds the six amounts, added in `core/`'s order, equal to it exactly. The end state the brief names still holds: the total and its parts come from one source, and they cannot disagree. `ROADMAP.md` § "v0.7.0 - the schematic", Required scope entry 2, now says the same. This was the one clearly correct option, so it was taken rather than offered.

**What `PL-2881` settled for this build, 2026-11-01.** `docs/MODEL.md` § "The compartment schematic: what its heights, amounts and share bar assert" reads each amount from the snapshot's per-compartment record, and the share bar divides by `stored_agent_l`. So the record and the total must agree exactly, which the unit test above already requires.
