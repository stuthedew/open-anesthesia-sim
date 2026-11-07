---
id: PL-XVCG
title: 'Cut the v0.4.4 release: the exact matrix exponential and its re-derivations'
priority: P2
effort: S
status: done
classes: planning, docs
feature: planning-cadence
milestone: v0.4.5
added: 2026-09-06
closed: 2026-09-06
pr: 379
not-delegable: proving a release cut means cutting the release. No command can run beforehand - `make release` refuses while the previous version is untagged, and the version-table row, baseline mark and release prose it stops short of are judged by a reader rather than by a check
---

**Problem.** Cut the v0.4.4 release: the exact matrix exponential and its re-derivations

**Why it matters.**

**Where.**

**Done when.**

**Done 2026-09-06.** Thirteen items since 0.4.3. `make release VERSION=0.4.4`
bumped `pyproject.toml`, relocked `uv.lock` and wrote `docs/releases/v0.4.4.md`;
the ROADMAP version-table row, the moved `current baseline` mark, the new
baseline section and the `### v0.4.4` release narrative are the hand half.

The version is a patch and stays one: `ROADMAP.md`'s `v0.4.x` row already
settles that the exact step crosses no capability boundary. What it does cross,
and what the prose leads on, is that a displayed number moves in its last digit
- the first release since v0.4.0 where that is true, and the first to touch
`src/` in four.

The `v0.4.x` track is **not** finished by this release. `PL-GS5X`, `PL-3TLK`
and `PL-X9KD` are done; the `core-domain-language` naming items (`PL-H46J`,
`PL-212V`, `PL-9SH6`, `PL-VZL0`, `PL-FZ6T`, `PL-X2XX`) remain, so the row keeps
its place in the plan.

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.4.4 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> The first release in four to touch `src/`, and the first since v0.4.0 in which a displayed number moves. The operator split is gone: each step is now one exact propagation of the whole coupled nine-state system, `exp(AΔt)y`, with `core/governing_equations.py` assembling $`A`$ as a transcription of the balance equations this document states and `core/matrix_exponential.py` computing the propagator without carrying a unit or a compartment name. Scaling and squaring with a shifted Taylor series, about sixty lines of arithmetic on plain lists, adding no dependency. **Accuracy was not the motivation and was not a cost either** — the split was kept once on accuracy, in 2026-08-30, and that decision was right on its own terms; what overturned it was `ROADMAP.md` item 29's bar, that a reviewer who knows the standard variables should follow `core/` without a lookup table. Three of the split's five composed sub-steps were objects of the splitting scheme rather than of the physiology, the alveolar balance's two terms were computed in different sub-steps separated by a third, and the pulmonary uptake rate this document specifies was never formed at all. Measured against the same from-scratch RK4 oracle, the exponential's worst disagreement is eight orders of magnitude smaller than the split's. **Then the harder half, which is what the release is really about.** Three published statements were derived from an error that no longer exists, and each is re-derived from measurement rather than assumed to still hold. § "Displayed precision" had a numerical ceiling (a third decimal was noise) and a legibility floor; the ceiling is gone, since the shipped residual is about 1.6e-12 percentage points, nine orders below the last displayed digit. Its replacement is **model fidelity**: one published standard deviation of a partition coefficient displaces a displayed compartment by 8.7e-4 to 6.8e-2 percentage points, so two decimals puts the last digit between a seventh of one SD and seven times it and a third would put it at a seventieth — false precision. `MAXIMUM_SIMULATION_STEP_S` turned out to have **no derivation at all**: sweeping the step from 1e-3 s to 1e300 s found no numerical ceiling, the propagator entrywise nonnegative at every one of 4374 (settings, step) combinations tested, and control-timing displacement exactly proportional to the step with no knee anywhere — so it is recorded as a *declared tolerance* in percentage points and seconds, not dressed up as a limit. And the splitting-error constants are retired with their reasons recorded in place, after checking coverage rather than after the fact: two of the four retiring tests were reproduced exactly by the new gate, two were not, so the step gate gained the setting-change trajectories and a new `HELD_RUN_ROUNDING_BOUND` replaced the only test driving the shipped solver past 900 s. **The dependency stopped running backwards.** The step bound and the supported input ranges were both justified *through* the two-decimal readout, so a purely presentational move to one decimal would have licensed a step ten times longer; both are now stated in their own units, and a test fails if anything in `core/` reads the display count again. `src/anesthesia_sim/data/` is byte-identical to v0.4.3, so no parameter moved — what moved is the method, and the displayed value in its last digit. Thirteen items, one of which is the v0.4.3 cut itself.
