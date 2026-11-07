---
id: PL-F1SZ
title: Cut v0.4.35 from the 16 items finished since v0.4.34: the release where a bookmark stops the run on the step that crosses it, and what a comparison against Gas Man is worth got written down by phase
priority: P2
effort: S
status: done
classes: housekeeping
feature: release-process
milestone: v0.5.0
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items
added: 2026-09-20
closed: 2026-09-20
pr: 778
payoff: clears the release the session-start digest re-raises in every session, and unblocks the next cut, which docket refuses while a release is untagged
verify: grep -q '^version = "0.4.35"' pyproject.toml
---

**Problem.** Cut v0.4.35 from the 16 items finished since v0.4.34: the release where a bookmark stops the run on the step that crosses it, and what a comparison against Gas Man is worth got written down by phase

The sixteen are **one product item** - `PL-CTD7`, `P1`/`safety`, bookmark
crossing detected inside the advance loop - **two model-boundary statements**
in `docs/MODEL.md` (`PL-D126` and `PL-WJNS`, both `P1`/`science`), **the whole
of `gate-list-integrity`** (`PL-0VFF`, `PL-82B0`, `PL-880Z`, `PL-B8V1`,
`PL-HJZW`, `PL-KF0T`, with `PL-S6RS` the regroup that named the feature and
`PL-R0P3` and `PL-NLP4` beside it), two anesthesia-machine scope items
(`PL-77G2`, `PL-6WNZ`), `PL-YD6X`, and `PL-Y3XK`, the v0.4.34 cut itself.
`PL-TBMX` is dropped in the same commit rather than finished, so it is not in
the notes. All sixteen are merged on `origin/main` at `9335196`; `v0.4.34` is
cut and tagged on the remote (`bf5c1f2`, commit `8c83951`), so nothing is
outstanding from the previous release.

**`0.4.35` is the number, and unlike the last four cuts only one half of
§ "Versioning decision"'s test carries it.** Every number above it is spent -
`ROADMAP.md` gives `0.5.0` to "the case you can branch", whose `Required
scope` still has `PL-49R8`, `PL-B8MK`, `PL-Z3W6`, `PL-VKJW` and `PL-W7H9`
open, and `0.6.0` through `0.9.0` to milestone sections of their own. The
capability half is weaker than in `v0.4.34`, and the item says so rather than
asserting that nothing moved: `PL-CTD7` is the first release in which a
bookmark *does* anything. A threshold or time mark now halts the run on the
step that crosses it, at every playback multiplier, and leaves it paused. That
is a boundary a learner can feel. It is released as a patch because the
minor that would mark it is reserved for the milestone it is scope for, and
shipping `0.5.0` with five of its nineteen `Required scope` ids open would
name that milestone for work that is not in it.

**The claim this cut owes a measurement is that nothing computational moved,
and `tests/reference/` moves here for the first time since `v0.4.29`** - so
the published-reference argument cannot be made by tree identity alone and is
made by reading the diff:

- `src/anesthesia_sim/core/` resolves to `0c8e708` at both `v0.4.34` and
  `HEAD`, and `src/anesthesia_sim/data/` to `ab3499f` at both, so no equation,
  parameter, constant, numerical method or stored scientific value changed.
- `tests/reference/` resolves to `fcb3eca` at `v0.4.34` and `5b43d4b` here.
  The whole of that is **four added lines of prose inside the module docstring
  of `test_published_wash_in_and_elimination.py`**, `PL-D126`'s cross-reference
  to `docs/MODEL.md` § "Known limitations". No expected value, tolerance or
  case is added, removed or changed, so every published-reference gate still
  holds at the same numbers.
- `src/anesthesia_sim/app/` resolves to `3bbe8a2` at `v0.4.34` and `87baee9`
  here: four files, +731/-30, all of it `PL-CTD7`. The release as a whole is
  49 files, +3,624/-230.

**The cut may also clear `pr:` backfills.** `bin/docket record` bare writes
every one the base can supply; let it ride the release commit rather than
composing one for it.

**Procedure**, from the `docket` skill's release mode, in order:

1. `make release VERSION=0.4.35` - never `bin/docket release` alone, which
   leaves `uv.lock` stale and fails the next `uv sync --locked`.
2. `bin/docket record` for any `pr:` backfill the base can supply.
3. The edits `bin/docket release` prints as outstanding: a `ROADMAP.md`
   version-table row, the `current baseline` mark moved onto it, and a
   baseline section saying what the release was for.
4. `make check`, which is what proves those edits landed.
5. Commit, push, open the pull request; the tag is the project owner's to run
   after the merge.

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.4.35 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> Sixteen items, and a patch on **one** half of § "Versioning decision"'s test rather than on both - stated rather than smoothed over. Every number above it is spent, v0.5.0 through v0.9.0 being given to milestone sections; but unlike the four patches before it this one is not a release in which nothing a learner can reach changed. `PL-CTD7` is the first release in which a bookmark *does* anything: until now a learner could write down the moment they cared about (v0.4.33, `PL-LPLD`) and the run would go straight past it. The number that would mark that is v0.5.0, which this roadmap gives to "the case you can branch" and whose `Required scope` still has five of nineteen ids open - and `PL-CTD7` is one of that milestone's own entries, so naming the milestone for a release holding one item of it would be the worse error. **Nothing computational moved**, measured by tree object: `src/anesthesia_sim/core/` resolves to `0c8e708` at both ends and `src/anesthesia_sim/data/` to `ab3499f`, so no equation, parameter, constant, numerical method or stored scientific value changed; `src/anesthesia_sim/app/` resolves to `3bbe8a2` and `87baee9`, four files, +731/-30, all of it `PL-CTD7`. **`tests/reference/` moves for the first time since v0.4.29 and no expected value moves with it** - `fcb3eca` to `5b43d4b`, the whole of it four added lines of prose inside the module docstring of `test_published_wash_in_and_elimination.py`, `PL-D126`'s cross-reference to § "Known limitations", with no case, expected value or tolerance added, removed or changed. **`PL-CTD7` is `P1` and `safety`-classed because the alternative is a wrong displayed value rather than a missing feature**: a tick advances its whole burst with nothing between the steps, so a crossing tested once per rendered frame would halt the same mark at a different concentration depending on playback rate - up to 30 simulated seconds of overshoot at 300x - and two branches nominally taken "at 0.8 ×MAC" would open from two different states. The crossing is tested on every simulation step and the run halts on the step that crossed, at every rate; the halt leaves the run **paused**, because a halt is exact and a setting changed while playing first acts at a tick boundary; and a crossing is a transition between two steps rather than a comparison at one, since a run settled exactly on a marked height would satisfy an at-or-above test forever. `docs/MODEL.md` § "Halting on a marked crossing" states all three. **The outcome set shipped four-valued rather than the three the item specified**: a branch inherits its trunk's marks, so a time bookmark before the branch's own fork instant can never be reached going forward, and "not reached" would tell a learner to wait for something that cannot arrive - it reads "before this branch opened", while a mark still reachable says nothing at all. **It completes `model-boundary-statements`, 2 of 2**, both `P1`/`science` and both limits of a comparison rather than defects: `PL-D126` records that Gas Man's own prospective in-patient validation is materially worse through wash-in than maintenance (first 15 min MDPE 18% / MDAPE 21% on the FLOW-i and 7% / 13% on the Zeus, against 0% / 6% and -1% / 5% over the last 45 min; Candries, De Wolf, Hendrickx, *J Clin Monit Comput* 2022;36(6):1881-1890, PMID 35318567), so the phase in which this project's reference implementation is least accurate is the phase this project most displays; `PL-WJNS` records that the unconditional circuit exhaust is a **semi-closed circle's**, a Zeus in automatic controlled mode closing the surplus gas valve to prevent any loss of gas volume (Meyer et al., *Modern Anesthetics*, HEP vol. 182, Springer 2008, p. 465), which is the one machine variable reaching an equation rather than a coefficient. **With both closed the debt gate under v0.5.0 stands at 177 of 178**, its one open entry `PL-WZVZ` blocked on three items that are not themselves in the gate (`PL-1FT6`, `PL-R1WQ`, `PL-TH35`), so nothing is left that working the gate can clear and v0.5.0 is implementable. **It completes `gate-list-integrity`, 6 of 6**, one problem rather than six: `ROADMAP.md`'s bookkeeping had drifted from the store where a later session would have been told something false about what is outstanding - `PL-0VFF` (three "Declined to Gate 2" entries closed in v0.4.14 and still listed as deferred, with nothing distinguishing open from closed), `PL-KF0T` (item 33 calling three done items open debt), `PL-B8V1` and `PL-NLP4` (present-tense counts true only on the day written) - and the checker had two defects of its own, `PL-82B0` (`_declined_ids` reading only the first subsection, silently orphaning the first's dispositions) and `PL-HJZW` (the gate-disposition failure printed as an advisory while the test made it a hard `make check` failure, so reading the label as optional pushed a red branch). `PL-R0P3` removes the third inline spelling of that same store read, `PL-880Z` repairs five ref-lifecycle briefs whose citations had moved, and `PL-S6RS` is the regroup that made the six one feature. `PL-77G2` and `PL-6WNZ` re-scope the anesthesia-machine work to the **framework alone** on the owner's instruction - item 1 keeps the interlock baseline, item 40 is a second profile loadable and refused where inadmissible with no chooser and no displayed value changing, which is what holds `PL-WZVZ`'s misattribution hazard inactive - and `PL-TBMX` is dropped, its premise refuted by the audit's own adversarial verifier. **It completes `settings-panel-prerequisite`, 2 of 2** with `PL-YD6X`, whose stated blocker described a tree `PL-2CS8` had already removed. `PL-Y3XK` is the v0.4.34 cut.
