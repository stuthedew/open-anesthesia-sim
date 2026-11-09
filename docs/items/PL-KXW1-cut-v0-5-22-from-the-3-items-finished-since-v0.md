---
id: PL-KXW1
title: Cut v0.5.22 from the 3 items finished since v0.5.21
status: done
resource: release-train
added: 2026-10-03
closed: 2026-10-03
pr: 1293
verify: grep -q "^version = \"0.5.22\"" pyproject.toml
---

**Problem.** Cut v0.5.22 from the 3 items finished since v0.5.21

**Done 2026-10-03.** `make release VERSION=0.5.22` stamped the three items
finished since v0.5.21 - `PL-2MD9` (`#1291`), `PL-73ZN` and `PL-BMY5`
(`#1292`), the numerical-domain chain's ready Gate 2 entries - and wrote
`docs/releases/v0.5.22.md`; `ROADMAP.md` takes the row, the baseline mark and
the baseline section. All three are Gate 2 entries, putting the gate at 136
of 194 cleared, from 133 at v0.5.21. The version is the patch the digest
offered: no capability boundary is crossed, and `bin/docket wave` lists 0.6.0,
0.7.0 and 0.8.0 as spent. `data/`, `app/`, `tests/reference/`, `README.md` and
`.github/` resolve to the same trees on the v0.5.21 tag and on this cut;
`core/` does not, and `PL-2MD9` changes the numerical method, so its own
closing note said bit-identity could not be claimed for the canonical path.

**So the comparison was re-run, and its answer splits by path.** One script,
run on the v0.5.21 tag and on this cut, played 81 runs through
`SimulationController` - the three agents, three pairs of dial settings each,
three cardiac outputs and three fresh gas flows, with the dial changed at
minute 30 and closed at 50, the fresh gas flow raised to 10 L/min at 60 and
the cardiac output by 1 L/min at 70 - then forked each at its minute-30 change
and played the branch for 30 minutes with the dial set back, comparing every
value as `float.hex()`:

- The path a run plays is bit-identical: 0 of 7,371 per-minute samples differ
  (`capture_state()`, `state_vector()` and the whole snapshot hashed), and 0 of
  the 139,968 readout strings formatted from them. A 0.1 s step takes no
  squarings, measured at the widest supported flows (10 L/min fresh gas,
  10 L/min cardiac output, 12 L/min ventilation) for each agent.
- `RunDefinition.state_at`, the canonical path keyframes and fork openings are
  taken from, differs on 49,590 of 66,339 elements, worst 2.8e-12 relative and
  7.2e-11 L absolute, both on the cumulative delivered amount.
- `drawn_window`, the chart's read, differs at the same scale over three
  windows of each run and one of its branch; formatted with `format_percent`
  and `format_mac_multiple`, as the hover box prints, 0 of 1,815,696 strings
  differ.
- A branch's states differ by at most 2.6e-12 relative, and its concentration
  and MAC readouts are identical. Its accounting panel is not: the two
  residual lines (`format_agent_residual`, exponent form) differ on 1,885 of
  2,511 samples, none larger than 5.4e-11 L on either side, and
  `format_agent_volume` rounded a delivered amount sitting exactly on a 0.05 L
  tie the other way twice (desflurane at 6% and 0.5 L/min, 1.35 L: `1.3 L` on
  the tag, `1.4 L` here; isoflurane at 0.6% and 0.5 L/min, 0.15 L: `0.1 L`
  and `0.2 L`).

The script was a one-off and is not kept. Neither closure merged inside the
v0.5.21 tag (`git describe --contains` resolves neither merge), so no notes
take a tag-span pointer, and `tools/pr_body_check.py` found no squash commit
that lost its body. No tag step is filed: `.github/workflows/tag-release.yml`
tags the cut when this pull request merges (`PL-2FY6`).

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.5.22 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item. In the quote, § "Versioning decision" is `ROADMAP.md`'s.

> Three items, the ready product-lane Gate 2 entries of `numerical-domain`, and a patch on both halves of § "Versioning decision"'s test: no capability boundary is crossed, since the two new refusals and the new squaring cap sit past anything a supported input reaches, and v0.6.0 through v0.8.0 are given to milestone sections. **No equation, parameter or stored value moved, but the numerical method did, so the trajectories are bit-identical only on the path a run plays**: `core/` changes (`a4699af` to `aac50af`) because `matrix_exponential` writes an empty row of the system matrix as the identity's row before its squarings and refuses a propagator needing more than 32 of them (`PL-2MD9`), and because a `RunDefinition` or `SimulationState` handed a point past 24 hours is refused where it is built (`PL-73ZN`, `PL-BMY5`). Over 81 runs across the three agents, every one of 7,371 sampled states a run plays, and every readout formatted from them, is identical at both ends; the canonical path, the chart's drawn values and a branch, which opens from a canonical keyframe, move at the last bits, worst 2.8e-12 relative, and no concentration, MAC or hover value changes at the precision printed. What a learner can see change is a branch's accounting panel: its two residual lines, printed in exponent form, read different digits of the same floating-point noise, and a delivered amount sitting exactly on a 0.05 L tie can round the other way. `data/` (`2b4bd16`), `app/` (`70fe21e`), `tests/reference/` (`d655cc7`) and `README.md` (`3a8f16e`) resolve to the same trees. **All three are Gate 2 entries**, and the gate stands at 136 of 194 cleared, from 133 at v0.5.21; `PL-KXW1`, the cut, ships in no release under `PL-KRS6`.
