---
id: PL-0F33
title: Cut v0.5.23 from the 204 items finished since v0.5.22
status: done
resource: release-train
added: 2026-10-11
closed: 2026-10-12
pr: 1422
verify: grep -q "^version = \"0.5.23\"" pyproject.toml
---

**Problem.** Cut v0.5.23 from the 204 items finished since v0.5.22

**Done 2026-10-12.** `make release VERSION=0.5.23` stamped the items finished
since v0.5.22 and wrote `docs/releases/v0.5.23.md`. It was re-run three
times as `main` moved under the draft, to take `PL-XJ22` (`#1416`),
`PL-Y3GK` (`#1418`) and `PL-QFFF` (`#1423`), so the cut holds 204 items where
the filing counted 201.
`ROADMAP.md` takes the row, the baseline mark and the baseline section. 54 are
Gate 2 entries, putting the gate at 194 of 222 cleared, from 136 of 194 at
v0.5.22. The version is the patch the project owner chose ("Cut now",
2026-10-11): no capability boundary is crossed, and `bin/docket wave` lists
0.6.0, 0.7.0 and 0.8.0 as spent. Every tree moved except `README.md`, and
`data/` only in prose - four string fields, every number, boolean and key
unchanged - so the trajectory comparison was re-run.

**It found every sampled state bit-identical.** One script, run on the
v0.5.22 tag and on this cut, played 81 runs through `SimulationController` -
the three agents, three pairs of dial settings each, three cardiac outputs and
three fresh gas flows, with the dial changed at minute 30 and closed at 50,
the fresh gas flow raised to 10 L/min at 60 and the cardiac output by 1 L/min
at 70 - and a 30-minute branch from each at its minute-30 change. It drew
each as the chart does, in a following window every five minutes and in fixed
windows over the whole run, the change and the late washout, and ran each
agent's default case at the shipped 0.1 s step to 24 hours, comparing every
value by its exact bits:

- Nothing differs in 9,882 per-minute samples (`capture_state()`,
  `state_vector()` and every number in the snapshot), in 88,938 sampled
  elements of `RunDefinition.state_at`, in 15,846,273 drawn values at
  1,760,697 instants, or in 21,128,364 hover strings.
- Of 207,522 readout strings, 19,764 differ, every one on the accounting
  panel's two residual lines, which `PL-3PJZ` prints as the power of ten each
  lies below: `1.510e-14 L` on the tag, `<1e-13 L` here, and `0 L` for zero.
- Three 24-hour runs take 864,000 steps to 86,400 s on both trees, with all 26
  hourly states identical. Here the step that reaches 86,400 s leaves the run
  stopped with the limit's reason (`PL-5291`), where the tag read as running
  until the next step was refused.

The script was a one-off and is not kept. No closure merged inside the
v0.5.22 tag, so no notes take a tag-span pointer; every bullet cites its pull
request, and `tools/pr_body_check.py` found no squash commit that lost its
body. No tag step is filed: `.github/workflows/tag-release.yml` tags the cut
when this pull request merges (`PL-2FY6`).
