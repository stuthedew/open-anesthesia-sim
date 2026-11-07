---
id: PL-MHYG
title: "Cut v0.4.22: the release where what this project says about itself was checked against what is true"
priority: P2
effort: S
status: done
classes: planning, docs
feature: release-process
milestone: v0.4.23
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items/
added: 2026-09-14
closed: 2026-09-14
pr: 554
verify: python3 tools/doc_check.py check && grep -q '^version = "0.4.22"' pyproject.toml && test -f docs/releases/v0.4.22.md
---

**Problem.** Cut v0.4.22: the release where what this project says about itself was checked against what is true

**Fifteen finished items since v0.4.21**, offered and approved by the project
owner on 2026-09-14. `v0.4.21` was confirmed tagged on the remote before the
cut, so `bin/docket release`'s refusal-on-untagged-predecessor did not apply.

**A patch, and the version policy is why.** § "Versioning decision" chooses the
number for the capability boundary a release crosses, and this crosses none:
nothing a learner can do changed, and nothing a reader of the simulator sees
changed. That is measured rather than asserted - `src/anesthesia_sim/app/`,
`tests/reference/` and `.github/` resolve to the same tree objects as at
`v0.4.21` (`7586231`, `e519afd`, `5aa42db`), and the whole of `src/` differs in
two files, neither of which moves a number: a docstring on
`core/alveolar.py` and one `sources` entry plus a rewritten `provenance_gap` on
`data/machines/reference_circle_system.json`.

**What the release is about**, in one line each, is in `ROADMAP.md`'s
`v0.4.22` version-table row under § "Versioning decision" - it was the current
baseline when this item closed, and `v0.4.23` has since taken that heading: the
specification stopped saying a measurement had
not been sought (`PL-QBKQ`, `PL-XWCY`, `PL-DJYF`); what a number says when
nothing around it qualifies it (`PL-YLKR`, `PL-DNHM`, `PL-3M3K`); and nine
apparatus items, one of which recommended destroying work (`PL-8M8H`).

**One session was waiting on the same decision and could not be told.**
`session_01LVX9BVkhKGUjMgTe2bkwwL` - the `PL-GLBF, PL-J7C5, PL-PGZK, PL-8M8H,
PL-028F` gate batch - was running with "awaiting merge + v0.4.22 cut decision"
as its state when this cut began. It is a separate container, so `SendMessage`
could not reach it; `ListAgents` reports no peer on this machine. What guards
the collision is `bin/docket release`'s own refusal on an unmerged ref carrying
a cut, which is why this branch was pushed as soon as the cut existed rather
than at the end. `PL-66FP` is the precedent - two sessions cut v0.3.7
independently and the second was discarded at the merge.

**Why it matters.** A release cut that is not recorded as an item is invisible
to every in-flight guard this project has, all of which match a `PL-` id, and
the cut is the one piece of repository work most likely to be started twice -
the session-start digest offers it to every session at once. Filing it first is
`CLAUDE.md`'s housekeeping rule, and the collision above is the reason that rule
exists.

**Done when** `pyproject.toml` reads `0.4.22`, `uv.lock` agrees,
`docs/releases/v0.4.22.md` exists with the fifteen items stamped,
`ROADMAP.md` carries the version-table row and the baseline section, and
`make check` is green. The tag is not part of this item: only the project owner
can push a tag ref from this environment, so it is filed separately.

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.4.22 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item. In the quote, § "Displayed precision" is `docs/MODEL.md`'s.

> Nothing a reader of the simulator sees changed, and that is measured rather than asserted: `src/anesthesia_sim/app/`, `tests/reference/` and `.github/` resolve to the same tree objects as at `v0.4.21` (`7586231`, `e519afd`, `5aa42db`), so no interface element, no pinned reference state and no CI gate moved. The whole of `src/` changes in two files and neither changes a number - `core/alveolar.py` gains a docstring, `data/machines/reference_circle_system.json` gains one `sources` entry and a rewritten `provenance_gap` - so `2.5`, `4.0` and `6.0` stand where they stood, and no equation, parameter, unit, numerical method or solver step is touched. **The science half is the specification understating what it knows.** `PL-QBKQ`: `reference_circle_system.json` said a measured circle-system volume "has not been sought yet", and one had been - Targ, Yasuda and Eger's 9860 ml by water filling, which does *not* close the gap because it includes a latex reservoir bag standing in for the patient's lungs, and the apparatus's own share cannot be recovered from a volume obtained by filling that bag with water. What it supplies is a measured **upper bound**, ordering three figures of which one is measured: this project's 6.0 L, Gas Man's published 8.0 L, and that 9.86 L. The like-for-like comparison is the one to read - apparatus plus lung is 6.0 + 2.5 = 8.5 L against 9.86, 13.8% below, where the bare 6.0 reads as 39% below. `PL-XWCY`: the same paper strikes circuit-wall absorption as the cause of desflurane's washout residual and, in the same measurement, says a real circle system measurably retards sevoflurane and isoflurane relative to ideal - a named, quantified mechanism this model has no term for, bearing on cohorts already sitting at +3.79 and +4.15 SD. `PL-DJYF`: `AlveolarCompartment` restated the reference patient's 2.5 L and 4.0 L/min as dataclass defaults while `reference_adult.json` stored both with their provenance, the same restatement `PL-4YY1` found on `BreathingCircuit`; the docstring now names the file as the authority and a test fails if the two ever disagree, because a reader meeting `2.5` in `core/` will take it for the model's alveolar volume whatever the prose says. `PL-M85T` later made both required arguments and retired that test with the defaults. **The safety half is what a displayed value may say when nothing around it qualifies it.** `PL-YLKR` derives the chart's hover readout the way § "Displayed precision" derives the numeric readouts - three lines with the qualifiers ahead of the number, every number through `app/formatting.py`, the readouts' own resolution with the argument for a finer one answered rather than inherited, and which series answer at all. The measurement that decides it: `pyqtgraph.ScatterPlotItem` defaults `tip` to `'x: {x:.3g}\ny: {y:.3g}'`, which on the fat compartment at 48.3 s of a 1 MAC sevoflurane hour prints `3.52e-05` where the readout beside it says `<0.01%` - five decimal places past the derived resolution, no unit, on a chart carrying two axes a factor of two apart. Its build is split to `PL-YVHK` behind the port, which is also where the second finding lands: `ScatterPlotItem` ships `hoverable` set to `False` and a plotted line carries no hover at all, so a port silent about it *loses* the affordance rather than inheriting it (`PL-DNHM`), against a milestone whose definition of done is parity. `PL-3M3K` corrects the brief that said the paused-only restriction transfers whole to Qt; it was a property of Flet's per-frame per-point diff. **The apparatus half is commands answering confidently and wrongly.** `bin/docket branch` told a session whose pull request had already merged to merge the base in rather than restart, which is exactly the push that loses the work (`PL-8M8H`); `bin/docket concurrent` was dominated by `docs/MODEL.md` - 16 of one probe's 22 rule-outs shared only that file - so it refused nearly everything and discriminated nothing, and now groups the tier by path, rarest first, so the strong evidence reads as strong (`PL-PGZK`); work landing between a release cut and its merge sat inside the tag's span and outside its notes with nothing reconciling the two (`PL-028F`); `ROADMAP.md`'s subset counts were hand-maintained and unchecked, and the one a field can decide now is (`PL-GLBF`); the contrast table's reasons cited line numbers that drift, and now cite symbols (`PL-J7C5`); and `PL-16ZC` sat in the gate's clearable set with no deferral marker, so a session clearing the gate would have built a Flet control `v0.5.1` deletes (`PL-NR2K`). `PL-JYR4` closed by its branch merging rather than by work on it. Fifteen items, one of which is the v0.4.21 cut itself.
