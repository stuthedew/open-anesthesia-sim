---
id: PL-VLZT
title: Cut v0.4.10 - the release where the apparatus stopped being implicit
priority: P2
effort: S
status: done
classes: planning
feature: planning-cadence
milestone: v0.4.11
touches: ROADMAP.md, pyproject.toml, uv.lock, docs/releases/v0.4.10.md, docs/items
added: 2026-09-08
closed: 2026-09-08
pr: 467
not-delegable: Proving a release cut means cutting the release; there is no command that can run beforehand and fail.
---

**Problem.** Cut v0.4.10 - the release where the apparatus stopped being implicit

**What it is for.** Twelve items finished since v0.4.9 and none of them moves a
stored value: `src/anesthesia_sim/data/` changes only in what its entries say
about their own numbers, and `core/` only in `circuit.py`'s docstrings. What
they have in common is the apparatus around the model - what a flow number
counts (`PL-CXYT`, `PL-71CF`), at what altitude and on which class of vaporizer
(`PL-5K5C`), through which breathing circuit (`PL-W21J`, `PL-73G7`), under
which identity the interface shows it (`PL-61WW`, `PL-97VB`), and out of which
book each parameter came (`PL-7HDS`, `PL-X19T`, `PL-J302`) - each of which was
already true and stated nowhere its reader would meet it. `PL-KTKP` closes
beside them.

**The one displayed change** is `PL-71CF`'s second label line under the
fresh-gas-flow control, which is the reason this is a release rather than a
docs pass: a user reading that control as a flowmeter mis-sizes the circuit
time constant by up to 22% at desflurane's dial maximum.

**Filed before the work under `CLAUDE.md`'s housekeeping rule**, which requires
repository work no item names to carry an id before it starts, because every
in-flight guard this project has matches a `PL-` id.


**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.4.10 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> No stored value moves: `src/anesthesia_sim/data/` changes only in what its entries say about their own numbers, and `core/` only in `circuit.py`'s docstrings. What moved is that the machine around the model - what a flow number counts, at what altitude, on which class of vaporizer, through which breathing circuit, and out of which book each parameter came - is now stated where a reader meets it. **Fresh gas flow was never the flowmeter setting.** The model reads it as flow at the common gas outlet, carrier gas plus the vapour the vaporizer added, and the two differ by `1/(1 - F_D)` - 22% at desflurane's 18% dial maximum. `docs/MODEL.md` and `BreathingCircuit` now say so (`PL-CXYT`), and so does the one place a user actually reads: the control carries "common gas outlet" as a smaller second line under its label, in the idiom the metric panels already use for "Alveolar / end-tidal-equivalent" (`PL-71CF`). The user-visible consequence is the circuit time constant `V_C/V_F`, which is what the wash-in curve is about. **The model is at sea level, and the delivered-concentration dial is a class of vaporizer rather than a universal control** (`PL-5K5C`) - both recorded rather than assumed. **The elimination comparison was measuring a breathing circuit, and now says how much.** `tests/reference/test_published_wash_in_and_elimination.py` gained a test-only open-circuit driver that discards the circuit after every step of the washout and records the agent as exhausted, which is the condition Yasuda's expirate collection ran at and one no setting of this simulator reaches; the apparatus is worth **3.5 to 4.2 published SD** per cohort, and with it removed sevoflurane and both isoflurane cohorts land inside the published spread that the shipped condition missed by +3.8 to +5.1 SD (`PL-W21J`). Desflurane crosses to 2.33 SD on the *other* side, and `PL-73G7` records that as a disagreement no parameter closes rather than one to tune away. **Agent identity had been reaching the screen in Material's disabled grey** - fixed on the running-agent control (`PL-61WW`), with the general rule for every identity-carrying control decided and left as one check to build (`PL-97VB`). **Lowe and Ernst 1981 was read at the source**, by interlibrary loan: page 56 says the figure's volumes and flows are collected and cited onward, so the book is tier 2, nothing is promoted or adopted, and of the seven values the Gas Man Workbook credits to it three reproduce and four do not (`PL-7HDS`). **And the resident provenance rule was contradicting the shipped parameter set.** "A reference implementation is never the authority for a constant" loads in every session, while twelve partition coefficients and ten of the reference patient's eleven parameters are adopted from one on a recorded decision; the letter now says what the spirit always did, which is never a *silent* authority (`PL-X19T`, `PL-J302`). `PL-KTKP` closes beside them: the v0.5.0 debt gate had under-reported by eleven safety- and science-classed entries for two days, and those eleven were the whole of its `P1` band. Twelve items, one of which is the v0.4.9 cut itself.
