---
id: PL-5VR1
title: "Cut the v0.4.6 release: provenance read at the source"
priority: P2
effort: S
status: done
classes: planning
feature: release-process
milestone: v0.4.7
touches: ROADMAP.md, pyproject.toml, uv.lock, docs/releases
added: 2026-09-06
closed: 2026-09-06
pr: 411
not-delegable: proving a release-time change means cutting a release; there is no command that can be run beforehand
---

**Problem.** Eleven items finished since v0.4.5 with no release behind them,
and `bin/docket wave` read the beat as clearing Gate 1 while the digest offered
0.4.6 in every session.

**Why it matters.** `bin/docket release` refuses to cut while the previous
release is untagged, and `milestone:` stamping is what lets a later reader ask
what shipped when. Unshipped finished work also makes the digest's release
offer repeat in every session until somebody acts on it.

**Where.** `pyproject.toml` and `uv.lock` (the version), `docs/releases/v0.4.6.md`
(generated), and `ROADMAP.md` - the version-table row, the `current baseline`
mark moved off v0.4.5, the baseline section rewritten, and a release-narrative
entry added.

**Approach.** `make release VERSION=0.4.6`, never `bin/docket release` alone -
the tool writes the version into `pyproject.toml` and stops, and `uv.lock`
records the project's own version too, so the next `make check` fails on `uv
sync --locked` with the tree half-updated. Then the prose the tool does not
generate, then `make check`.

**Done, 2026-09-06.** Cut on the project owner's instruction after the
recommendation to hold was overtaken: the five parallel sessions that argued
for waiting had all landed. The version was named rather than incremented, per
`ROADMAP.md`'s "Versioning decision"; 0.4.6 was also the mechanical guess,
because this release crosses no capability boundary - it is gate-clearing and
provenance work inside the `v0.4.x` track.

Eleven items stamped. `src/anesthesia_sim/core/` is byte-identical to v0.4.5
and every stored value in `src/anesthesia_sim/data/` is unchanged; the only
`src/` changes are three `app/` files from `PL-GYH2`. Gate 1 stands at 17 of
121 cleared.

**The tag is outstanding and is the project owner's to run** - a session cannot
push a tag ref from this environment (`PL-N936`: `git push --dry-run` reports
`[new tag]` and the real push dies on `send-pack: unexpected disconnect` while
`git ls-remote --tags` shows nothing). The commands are in the closing block of
the reply that cut it, filled in against the merge commit.

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.4.6 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> `src/anesthesia_sim/core/` is byte-identical to v0.4.5 and every stored value in `src/anesthesia_sim/data/` is unchanged, so no equation, parameter, numerical method, solver step or displayed value moved; what changed under `data/` is entirely what the citations claim. **The reference patient's numbers had never been traced to a document anybody opened.** `PL-6Q8N` set out to read Mapleson's 1963, 1964 and 1973 papers, named in the file as its primary lineage — and found them unreachable from a session: all three return PubMed metadata only, none has an abstract, none is in PMC, and every publisher, index and vendor route is refused by the egress proxy. Re-aimed on the project owner's decision at what PubMed can actually deliver, five of the eleven parameters gained a measurement of the same quantity cited alongside and explicitly *not* adopted — Hudgel and Devadatta's helium-dilution FRC read with Wahba's ~20% reduction under general anaesthesia brackets the lung gas volume at 2.51 L against a stored 2.5; Cattermole et al.'s 686 subjects in the 50–75 kg band give a cardiac-output median of 5.51 L/min against a stored value 9.3% below it; Janssen et al.'s whole-body MRI gives a skeletal-muscle mass whose apparent agreement with the stored 33.0 is *coincidence*, that cohort of men having averaged about 86 kg rather than 70; and Heinonen et al.'s PET measurement of resting adipose perfusion is close to half what the stored fat flow fraction implies. The other six record why no comparison exists rather than leaving the silence to read as an oversight. The fat gap is the one that reaches a learner: time constant is `V·λ/Q`, so a factor of two on fat flow is a factor of two on how much agent fat has taken up by the end of a case and on the slow tail of every washout curve — recorded in `docs/MODEL.md` § "Known limitations" rather than fixed, because one depot in six subjects does not overturn a whole-body lumped compartment. **Then the project owner supplied the Gas Man Workbook, and the guess collapsed.** `PL-XTMB` read it at the source: the Model Parameters table is Appendix B, page 168, and the citation had been pointing at page 183's interface controls, which carry none of the values. The file's own claim to be sourced entirely from that table was false — it supplies **seven of the eleven**; cardiac output appears only as the sum of the flow column; weight and alveolar ventilation are interface defaults with no number in it; and `venous_blood_volume_l` = 1.0 is absent altogether, the table's `Blood` row reading 5.00 L, which leaves a stored value its cited source does not contain (`PL-3YZW`). And the lineage is not Mapleson at all: printed beneath the table, *"Values for volume, flow and relative flow are taken from Lowe and Ernst, 1981"*. That book is recorded as located and unread, inside the Workbook's own note rather than as a citation line of its own — an unread document with its own entry is the Mapleson failure one link later, and the schema made the point first by refusing the empty `url` a 1981 monograph would need. **Three checks were measuring something other than what they claimed.** `tools/contrast_check.py` cited `simulation_view` line numbers for its eight requirements and all eight were wrong, and it could not express a requirement met by either of two channels at all; the mass-balance release gate's absolute tolerance tracked whichever dial its test happened to run at rather than a stated bound; and `docket.toml`'s `workflow_paths` named three `tools` tests by path, so the other seven and every new one fell on the product side of the lane boundary that exists to keep two sessions apart. **Two queue mechanics and one model-boundary correction** close beside them: the closure walk follows renames, so an item renamed after it closed no longer recovers the renaming commit's pull request; the conflict graph is tiered, so a shared file orders work instead of forbidding it — which matters because 27 of Gate 1's entries declare `docs/MODEL.md`; and `SimulationController.set_circuit_volume` is gone, both gas volumes established as data-file parameters rather than controls, with the bound restated on physiological rather than numerical grounds. That restatement then produced the release's third correction: `PL-GYH2` had landed the sentence "the exact propagator solves the governing equations for any positive volumes whatever", written from the argument rather than from a measurement, and run it is false — below 1e-9 L the alveolar compartment raises, at 1e-100 L the step rolls back, and at 1e-300 L it advances and returns exactly zero with the accounting passing. `PL-GJYL` replaced it with the measured statement. **And the first comparison in the elimination direction.** `PL-HB58` extended the project's only external validation to the second quantity both Yasuda papers report on the same volunteers, $`F_A/F_{A0}`$ at five minutes of elimination — and it does not agree: the model holds more alveolar agent at five minutes than every cohort did, by +1.0 to +5.0 published SD. Most of that is apparatus rather than physiology, and it is measured rather than argued: $`F_A/F_I`$ carries the inspired fraction in its denominator so a breathing system divides out of it, $`F_A/F_{A0}`$ has no such term, and this model's rebreathing circuit cannot be set below about 29% of the alveolar fraction at any supported flow — so agent returning from the circuit is counted as though it came back out of the patient. The values are therefore asserted as a *regression* band that claims nothing about agreement, while the published ordering by solubility, the independence from delivered fraction and the sign of the departure are asserted as the validations they are. What the second direction buys is a different axis rather than a tighter one: the wash-in comparison and its flow sweep were still passing at a tenth of the shipped vessel-rich tissue coefficient, and the elimination point closes that tolerance to about a fifth either way. Thirteen items, one of which is the v0.4.5 cut itself.
