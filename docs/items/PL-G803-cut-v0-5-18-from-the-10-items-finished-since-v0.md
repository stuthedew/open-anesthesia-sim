---
id: PL-G803
title: Cut v0.5.18 from the 10 items finished since v0.5.17
status: done
resource: release-train
added: 2026-09-30
closed: 2026-09-30
pr: 1236
verify: grep -q "^version = \"0.5.18\"" pyproject.toml
---

**Problem.** Cut v0.5.18 from the 10 items finished since v0.5.17

**Done 2026-09-30.** `make release VERSION=0.5.18` stamped the ten items and
wrote `docs/releases/v0.5.18.md`; `ROADMAP.md` takes the row, the baseline
mark and the baseline section. No stored number moved (every numeric field
in `src/anesthesia_sim/data/` compared at both ends: only `schema_version`,
2 to 3), and 5,040 state vectors sampled once a minute over 60 minutes across
three agents, nine cardiac outputs and three fresh gas flows, plus each
agent's opening flow, hash identically on v0.5.17 and on this cut. Before
filing, `bin/docket flight` and `list_sessions` showed no other session
holding the release train or cutting, and none of the eight in-flight
branches edits any of the ten items. `make check` passed: 5,672 tests,
100% core coverage. The tag step is `PL-Y65G`.

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.5.18 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item. In the quote, § "Versioning decision" is `ROADMAP.md`'s.

> Ten items, and a patch on both halves of § "Versioning decision"'s test: nothing a learner can reach looks different, and v0.6.0 through v0.8.0 are given to milestone sections. **No equation, parameter or stored value moved, and the trajectories are bit-identical**: every number in `data/` is unchanged, and the data files move (`b8477a1` to `2b4bd16`) only by schema version 3 and a new `authority_for` on each source entry, naming the stored values that entry is the authority for; `core/parameters.py` validates it, and `tools/source_tier_counts.py` prints the per-tier counts in `docs/MODEL.md` from it (`PL-9LXK`). The Yasuda, Targ and Eger entry in all three agent files stops opening "cited but not adopted" (`PL-R1VD`). 5,040 states sampled once a minute across the three agents, nine cardiac outputs and three fresh gas flows, and each agent's own opening flow, hash identically at both ends. The other eight are workflow tooling. Six are Gate 2 entries, and the gate stands at 115 of 194 cleared.
